# -*- coding: utf-8 -*-

import errno
import os
import os.path


HERE = os.path.dirname(__file__)


def force_symlink(source, link_name):
    try:
        os.symlink(source, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.unlink(link_name)
            os.symlink(source, link_name)
        else:
            raise


def link_config():
    private_dir = os.path.join(HERE, '..', 'private')
    if not os.path.isdir(private_dir):
        print('Cannot find private dir, you can link your config files manually.')
        return

    conf_dir = os.path.abspath(os.path.join(HERE, '..', 'conf'))
    private_conf_dir = os.path.join(private_dir, 'conf')
    for conf_name in os.listdir(private_conf_dir):
        force_symlink(os.path.join('../private/conf', conf_name), os.path.join(conf_dir, conf_name))

    config_dir = os.path.abspath(os.path.join(HERE, '..', 'doodle', 'config'))
    private_config_dir = os.path.join(private_dir, 'config')
    for config_name in os.listdir(private_config_dir):
        if config_name.endswith('.py') and config_name != '__init__.py':
            force_symlink(os.path.join('../../private/config', config_name), os.path.join(config_dir, config_name))


def mkdir(path, recursive=False):
    try:
        if recursive:
            os.makedirs(path)
        else:
            os.mkdir(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def create_dirs():
    log_dir = os.path.join(HERE, '..', 'logs')
    mkdir(log_dir)

    data_dir = os.path.join(HERE, '..', 'data')
    mkdir(data_dir)

    dropbox_redis_dir = os.path.expanduser('~/Dropbox/doodle/redis')
    redis_dir = os.path.join(HERE, '..', 'data', 'redis')
    if os.path.isdir(dropbox_redis_dir):
        force_symlink(dropbox_redis_dir, redis_dir)
    else:
        mkdir(redis_dir)


def install():
    link_config()
    create_dirs()
