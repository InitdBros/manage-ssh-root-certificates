Este script permite administrar manual y centralizadamente todos las llaves ssh root de nuestra infraestructura definida
en el archivo servers.json. 

La estructura definida en dicho archivo es la siguiente, y es la que debe modificarse según las necesidades de la infraestructura:

    {
      "servidores" : [
        {
          "ip" : "198.199.67.78",
          "user" : "root",
          "certificate" : "/home/fidel/.ssh/rootcertificate-221020-test.pub"
        }
      ]
    }


DINAMICA DEL SCRIPT: 

El script funciona de manera interactiva con quien lo ejecuta, y solicita el ingreso por teclado de los datos necesarios para generar la nueva llave: 
  
  
  1- Lo primero que hace es preguntar si queremos crear un nuevo certificado.
  
        Desea crear el nuevo certificado? (yes/no) *Ingresar yes o no*
   
  2- Luego nos pregunta para quien es el certificado.
        
        Para quien es el certificado? *Ingresar nombre*
        
  3- Por ultimo nos indica la ip del servidor a la cual nos urge conectarnos: 
    
        Ingrese la ip del servidor: *Ingresar ip del servidor, en el siguiente formato: 198.199.67.78*
  
  
 Luego de la carga de datos el script realizará los siguientes pasos: 
 
a. Generación de la nueva llave ssh. 
 
b. Backup de la llave ssh existente en el servidor al cual nos queremos conectar. Se hace un cp del authorized_keys hacia authorized_keys.bkp 

* En caso de ya existir un authorized_keys.bkp nos pregunta si queremos pisarlo por el nuevo archivo authorized_keys.bkpb
    
c. Envía el certificado al nuevo servidor, agregando en el archivo authorized_keys la nueva llave ssh. Ya que si solamente PISAMOS el archivo authorized_keys y la conexión falla por un motivo X, no tenemos la posibilidad de hacer un rollback. 

d. Luego de enviar el certificado, se hace un testeo de conexión hacia el servidor, el cual nos indica si nos podemos conectar de forma correcta con el nuevo certificado o no. 

e. En caso de dar error el testeo de conexión con el nuevo certificado, automaticamente se hace un rollback del proceso. 

f. Una vez validada la conexión, nos conectamos nuevamente al servidor de destino, y eliminamos el certificado viejo del archivo authorized_keys. 

g. Finalizado este proceso, el script actualiza en el archivo json.servers, el valor asignado al campo "certificate", con el full path de la nueva llave ssh generada localmente. De esta manera, la próxima vez que querramos generar un nuevo certificado para el mismo servidor, nos vamos a conectar utilizando la ultima llave generada para el mismo, y no una desactualizada con la cual no podrías tener acceso porque ya no estaría escrita en el authorized_keys. :) 
 
 
INSTALACIÓN DEL SCRIPT:

a. Clonar repositorio en maquina local desde la cual se manejarán los certificados. 

b. El script ./rollback.sh debe alojarse en el ~/ del servidor destino. 

c. Se requieren para ejecutar el script tener python3 instalado y las siguientes librerías dentro de python3:

      fileinput
      os
      datetime
      json

d. Situarse en el directorio donde se almacena el script, y escribir python3 script.py para comenzar a usarlo. 
 
