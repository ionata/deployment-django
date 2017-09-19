#!/usr/bin/env python3
# pylint: disable=expression-not-assigned
from os import environ, path
from pathlib import Path
from subprocess import run
from shutil import which
import sys


class Deployer:
    pre_deploy_actions = [
        'help',
        'self_update',
        'update',
    ]
    actions = pre_deploy_actions + [
        'celery',
        'gunicorn',
        'run',
        'run_dev',
    ]

    def __init__(self):
        self._get_paths()

    @property
    def _in_container(self):  # pylint: disable=no-self-use
        return path.exists('/.dockerenv')

    def _get_paths(self):
        self.deploy_script = path.realpath(__file__)
        self.deploy_root = path.dirname(self.deploy_script)
        self.deploy_marker = path.join(
            self.deploy_root, environ.get('DJCORE_APP_NAME', ''), '.deployed')
        self.deploy_env = path.join(self.deploy_root, '.env')
        self.deploy_venv = path.join(
            self.deploy_root, environ.get('DJCORE_APP_NAME', ''), 'venv')
        self.deploy_bin = path.join(self.deploy_venv, 'bin')
        self.root = path.dirname(self.deploy_root)
        self.project_root = path.realpath(
            environ.get('PROJECT_ROOT', path.join(self.root, 'backend')))
        self.project_env = path.join(self.project_root, '.env')
        self.project_venv = path.realpath(
            environ.get('PROJECT_VENV', path.join(self.root, 'venv')))
        self.project_bin = path.join(self.project_venv, 'bin')

    def _setup(self):
        import pip
        pip.main(['install', '--upgrade', 'python-dotenv'])
        try:
            from dotenv import load_dotenv
        except ImportError:
            self._rerun_in_venv()
            return
        for envfile in [self.deploy_env, self.project_env]:
            if path.exists(envfile):
                load_dotenv(envfile, override=True)

    @property
    def _in_venv(self):
        return environ.get('VIRTUAL_ENV') == self.deploy_venv

    def _create_venv(self, venv_dir):
        if not path.exists(path.join(venv_dir, 'bin', 'pip')):
            import venv
            venv.create(venv_dir, with_pip=True)
            self._update_venv(self.deploy_venv)

    def _update_venv(self, venv_dir):  # pylint: disable=no-self-use
        pip = path.join(venv_dir, 'bin', 'pip')
        cmd = '{} install --upgrade pip setuptools wheel'.format(pip).split(' ')
        run(cmd)

    def _rerun_in_venv(self):
        self._create_venv(self.deploy_venv)
        cmd = [path.join(self.deploy_bin, 'python3'), self.deploy_script] + sys.argv[1:]
        self.run(cmd, False, env={**environ.copy(), **{'VIRTUAL_ENV': self.deploy_venv}})

    def _get_conf(self, conf):  # pylint: disable=no-self-use
        return (lambda x: x and x.split(' ') or [])(environ.get(conf, ''))

    def _run(self):
        action = (sys.argv[1:2] + ['help'])[0].replace('-', '_')
        func = getattr(self, action if action in self.actions else 'help')
        if action not in self.pre_deploy_actions and not path.exists(self.deploy_marker):
            print('Not deployed')
            return
        command = sys.argv[2:]
        if command:
            func(command)
        else:
            func()

    def deploy(self):
        if not self._in_venv:
            self._rerun_in_venv()
            return
        self._setup()
        self._run()

    def run(self, cmd, project_venv=True, **kwargs):
        env = kwargs.pop('env', None) or environ.copy()
        cmd = cmd.split(' ') if isinstance(cmd, str) else cmd
        if project_venv:
            self._create_venv(self.project_venv)
            env['VIRTUAL_ENV'] = self.project_venv
            if self.project_bin not in env['PATH']:
                env['PATH'] = ':'.join([self.project_bin, env['PATH']])
                environ['PATH'] = env['PATH']
        command = which(cmd[0])
        if command is None:
            print('{} is not on the path ({})'.format(cmd[0], env['PATH']))
            return
        cmd[0] = command
        print('> ' + ' '.join(cmd))
        run(cmd, env=env, **kwargs)

    def self_update(self):
        self._update_venv(self.deploy_venv)
        self.run('git pull') and self.run('git submodule update')

    def install(self):
        if not path.exists(path.join(self.project_root, 'setup.py')):
            self.run('pip install -e %s' % environ['DJCORE_GIT_REPO'])
            return
        self.run('pip install -e %s' % self.project_root)
        requirements = path.join(self.project_root, 'requirements.txt')
        if path.exists(requirements):
            self.run('pip install --upgrade -r %s' % requirements)

    def update(self):
        self._create_venv(self.project_venv)
        self._update_venv(self.project_venv)
        if path.exists(path.join(self.project_root, '.git')) and not self._in_container:
            git = 'git -C %s' % self.project_root
            self.run('%s pull' % git)
            self.run('%s submodule update' % git)
        self.install()
        self.run('django-admin collectstatic --noinput')
        self.run('django-admin migrate --noinput')
        self.run('django-admin setup_skeletons')
        if None not in (which('sudo'), which('systemctl')):
            self.run('sudo systemctl restart production_*')
        Path(self.deploy_marker).touch(exist_ok=True)

    def run_dev(self):
        self.run(['django-admin', 'runserver_plus', '--nopin', '0.0.0.0:8000'])

    def celery(self, cmd=None):
        self.run(['celery'] + self._get_conf('CELERY_CONF') + (cmd or []))

    def gunicorn(self, cmd=None):
        self.run(['gunicorn'] + self._get_conf('GUNICORN_CONF') + (cmd or []))

    def help(self):  # pylint: disable=no-self-use
        print('Please provide an option')


if __name__ == '__main__':
    Deployer().deploy()
