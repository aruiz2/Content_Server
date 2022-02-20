def print_uuid(parser_cf, threadLock):
    uuid_dict = {"uuid": parser_cf.uuid}
    threadLock.acquire()
    print(uuid_dict)
    threadLock.release()