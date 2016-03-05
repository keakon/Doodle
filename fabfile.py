# -*- coding: utf-8 -*-

from fabric.api import cd, env, lcd, local, run, task


env.use_ssh_config = True


@task
def get_code_branch():
    output = local('git branch', capture=True)
    for line in output.splitlines():
        if line[:2] == '* ':
            return line[2:]
    return 'master'


@task
def get_config_branch():
    with lcd('private'):
        output = local('git branch', capture=True)
        for line in output.splitlines():
            if line[:2] == '* ':
                return line[2:]
    return 'master'


@task
def update_code(branch='master'):
    with cd('/data/doodle'):
        run('git fetch --all')
        run('git checkout ' + branch)
        run('git reset --hard origin/' + branch)


@task
def update_config(branch='master'):
    with cd('/data/doodle/private'):
        run('git fetch --all')
        run('git checkout ' + branch)
        run('git reset --hard origin/' + branch)


@task
def restart():
    run('supervisorctl restart doodle:')


@task(default=True)
def fast_deploy():
    code_branch = get_code_branch()
    print('deploying %s code branch' % code_branch)
    update_code(code_branch)
    restart()


@task()
def deploy():
    code_branch = get_code_branch()
    config_branch = get_config_branch()
    print('deploying %s code branch and %s config branch' % (code_branch, config_branch))
    update_code(code_branch)
    update_config(config_branch)
    restart()
