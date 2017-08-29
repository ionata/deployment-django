#!/usr/bin/env python3
# pylint: disable=expression-not-assigned
from os import environ, path
from subprocess import run
import sys


class Deployer:
    actions = [
        'celery', 'help', 'gunicorn', 'run', 'run_dev', 'self_update', 'update',
    ]

    def __init__(self):
        self.deploy_script = path.realpath(__file__)
        self.deploy_root = path.dirname(self.deploy_script)
        self.deploy_marker = path.join(self.deploy_root, '.deployed')
        self.deploy_env = path.join(self.deploy_root, '.env')
        self.deploy_venv = path.join(self.deploy_root, 'venv')
        self.deploy_bin = path.join(self.deploy_root, 'venv', 'bin')
        self.project_root = path.dirname(self.deploy_root)
        self.project_env = path.join(self.project_root, 'src', '.env')
        self.project_venv = path.join(self.project_root, 'venv')
        self.project_bin = path.join(self.project_root, 'venv', 'bin')

    def _setup(self):
        import pip
        pip.main(['install', '--upgrade', 'python-dotenv'])
        from dotenv import load_dotenv
        load_dotenv(self.deploy_env)

    def _in_venv(self):
        return environ.get('VIRTUAL_ENV') == self.deploy_venv

    def _rerun_in_venv(self):
        import venv
        venv.create(self.deploy_venv, with_pip=True)
        cmd = [path.join(self.deploy_bin, 'python3'), self.deploy_script] + sys.argv[1:]
        self.run(cmd, False, env={**environ.copy(), **{'VIRTUAL_ENV': self.deploy_venv}})

    def _run(self):
        action = (sys.argv[1:2] + ['help'])[0].replace('-', '_')
        return getattr(self, action if action in self.actions else 'help')

    def deploy(self):
        if not self._in_venv:
            self._rerun_in_venv()
            return
        self._setup()
        self._run()

    def run(self, cmd, project_venv=True, **kwargs):
        env = kwargs.pop('env', None) or environ.copy()
        if project_venv:
            env['VIRTUAL_ENV'] = self.project_venv
            if self.project_bin not in sys.path:
                sys.path = self.project_bin + sys.path
        run(cmd.split(' ') if isinstance(cmd, str) else cmd, env=env, **kwargs)

    def self_update(self):
        self.run('git pull') and self.run('git submodule update')

    def run_dev(self):
        self.run(['django-admin', 'runserver_plus', '--nopin', '0.0.0.0:8000'])

    def help(self):  # pylint: disable=no-self-use
        print('Please provide an option')


if __name__ == '__main__':
    Deployer().deploy()
