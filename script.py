import fileinput
import os
import datetime
import json


def create_ssh_key(n):
    """
    Creamos el nuevo certificado localmente.
    key_name = string que contiene nombre de la nueva llave.
    :param n: nombre de la nueva llave ssh
    :return: La función retorna el full path de la nueva llave ssh generada.
    """

    print("\n\nComienzo de creación de llave SSH")
    x = datetime.datetime.now()
    date_certificate = x.strftime("%d%m%y")
    key_name = "rootcertificate-{}-{}".format(date_certificate, name)
    ssh_key_generated = "/home/fidel/.ssh/{}".format(key_name)
    os.system('ssh-keygen -t rsa -N "" -C {} -f {}'.format(key_name, ssh_key_generated))
    print("Fin de creación de llave.\n")

    return "{}.pub".format(ssh_key_generated)


def bkp_ssh_key(local_ssh, h):
    """
    :param local_ssh: llave local ssh con la que nos vamos a conectar al server remoto para hacer backup del auth_keys.
    :param h: host del servidor remoto.
    :return: la funcion no retorna valores.
    """
    print("Realizamos backup de la llave existente")
    user = "root"
    command_remote_server = "cp -piv ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bkp"
    os.system('ssh -o IdentitiesOnly=yes -i {} {}@{} "{}"'.format(local_ssh, user, h, command_remote_server))
    print("Fin de backup de la llave.")


def push_ssh_key(local_ssh, new_ssh, h):

    """
    :param local_ssh: llave local ssh con la que nos vamos a conectar al server remoto.
    :param new_ssh: nueva llave local generada en create_ssh.
    :param h: host remoto.
    :return: la funcion no retorna valores.
    """
    print("Enviamos el nuevo certificado a los servidores: ")
    user = "root"
    new_certificate = "/tmp/authorized_keys"
    stage_ssh_key = "cat {} > {}".format(new_ssh, new_certificate)
    send_certificate = 'scp -i {} {} {}@{}:~/'.format(local_ssh, new_certificate, user, h)
    add_certificate = "cat ~/authorized_keys >> ~/.ssh/authorized_keys"
    os.system(stage_ssh_key)
    os.system(send_certificate)
    os.system('ssh -o IdentitiesOnly=yes -i {} {}@{} "{}"'.format(local_ssh, user, h, add_certificate))
    print("Certificado actualizado.\n")


def drop_old_certificate(local_ssh, h):
    user = "root"
    delete_certificate_from_ak = "cat ~/authorized_keys > ~/.ssh/authorized_keys && rm ~/authorized_keys"
    os.system('ssh -o IdentitiesOnly=yes -i {} {}@{} "{}"'.format(local_ssh, user, h, delete_certificate_from_ak))
    print("Eliminamos el certificado anterior.")


def validate_certificate(ssh_key, h, local_ssh):
    print("Validamos la conexión:")
    user = "root"
    ssh_key_full_path_to_log = "{}.log".format(ssh_key)
    parser_ssk_key = ssh_key_full_path_to_log.replace(".pub", "")
    log_path = parser_ssk_key.split('/')
    full_log_path = "./logs/{}".format(log_path[4])
    os.system('touch {}'.format(full_log_path))
    command = 'ssh -q -o "BatchMode=yes" -i {} {}@{} "echo 2>&1" && echo ${} SSH_OK >> {} || echo ${} SSH_NOK >> {}'.format(
        ssh_key,
        user,
        h,
        h,
        full_log_path,
        h,
        full_log_path
    )
    os.system(command)

    with open("{}".format(full_log_path)) as f:
        for cnt, line in enumerate(f):
            line_split = line.split(' ')
            if line_split[1] == "SSH_OK\n":
                print("Test de conexión utilizando nuevo certificado Exitoso.")
                drop_old_certificate(local_ssh, h)
                update_json(ssh_key, h)
                return ssh_key
            else:
                print("Error en conexión al servidor utilizando nuevo certificado.\nRealizando rollback...")
                rollback(local_ssh, h)


def get_data(collected_data):
    with open('servers.json') as json_file:
        data = json.load(json_file)
        for p in data['servidores']:
            if p['ip'] == collected_data:
                return p['certificate']


def update_json(new_ssh, h):
    print("Realizamos update de nuestro archivo de configuración servers.json.")
    with open('servers.json') as json_file:
        data = json.load(json_file)
        for p in data['servidores']:
            if p['ip'] == h:
                old_certificate = p['certificate']
                new_certificate = new_ssh
                with fileinput.FileInput('servers.json', inplace=True, backup='.bak') as file:
                    for line in file:
                        print(line.replace(old_certificate, new_certificate), end='')

    print("Archivo servers.json actualizado.")


def rollback(local_ssh, h):
    user = "root"
    command_remote_server = "~/rollback.sh && ls -l .ssh"
    os.system('ssh -o IdentitiesOnly=yes -i {} {}@{} "{}"'.format(local_ssh, user, h, command_remote_server))


if __name__ == '__main__':

    while True:

        choice = input("Desea crear el nuevo certificado? (yes/no) ")

        if choice == "yes":

            name = input("Para quien es el certificado? ")
            host = input("Ingrese la ip del servidor: ")

            #   Obtenemos el full path de nuestro certificado local.
            local_ssh_key = get_data(host)

            #   Generamos el nuevo certificado.
            new_ssh_key = create_ssh_key(name)

            #   Realizamos backup del certificado ya existente en el servidor.
            bkp_ssh_key(local_ssh_key, host)

            #   Enviamos el nuevo certificado al servidor de destino.
            push_ssh_key(local_ssh_key, new_ssh_key, host)

            #   Validamos la conexión al nuevo servidor utilizando el nuevo certificado.
            validate_certificate(new_ssh_key, host, local_ssh_key)

            break

        elif choice == "no":
            print("Adios.")
            break
        else:
            print("Ingrese valor valido")
