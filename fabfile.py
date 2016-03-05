# -*- coding: utf-8 -*-

from fabric.api import cd, env, local, task, execute, run, runs_once


env.use_ssh_config = True


@task
def get_current_branch():
    output = local('git branch', capture=True)
    for line in output.splitlines():
        if line[:2] == '* ':
            return line[2:]
    return 'master'


@task
def update_code(branch='master'):
    with cd('/data/doodle'):
        run('git fetch -all')
        run('git checkout ' + branch)
        run('git reset --hard origin/' + branch)


@task
def update_config(branch='master'):
    with cd('/data/doodle/private'):
        run('git fetch -all')
        run('git checkout ' + branch)
        run('git reset --hard origin/' + branch)


@task
def restart():
    run('supervisorctl restart doodle:')


@task(default=True)
def fast_deploy():
    branch = get_current_branch()
    update_code(branch)
    restart()


@task(default=True)
def deploy():
    branch = get_current_branch()
    update_code(branch)
    update_config(branch)
    restart()
