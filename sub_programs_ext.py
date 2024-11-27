#!/usr/bin/python3


import argparse

#create user
def create_user(args):
    print(args.username)
    print(args)

#delete user
def del_user(args):
    print(args)

def get_parser():
    main_parser =argparse.ArgumentParser(prog="sample parser", usage="./sub_program.. [create_user]")

    #setup the sub programs
    subprograms = main_parser.add_subparsers()

    #adding the subprogram
    create_user_sp = subprograms.add_parser("create_user")
    create_user_sp.add_argument("-u", action="store", dest="username")
    create_user_sp.set_defaults(func=create_user)

    #adding the subprogram
    del_user_sp = subprograms.add_parser("del_user")
    del_user_sp.add_argument("username", action="store")
    del_user_sp.set_defaults(func=del_user)
    return  main_parser

try:
    m_parser = get_parser()
    res = m_parser.parse_args()

    if hasattr(res, "func"):
        res.func(res)

except Exception as ex:
    print(f"There was an error here: {ex}")
