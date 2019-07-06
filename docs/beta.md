3. Reales decretos personalizados.

Los reales decretos personalizados pueden ser creados y eliminados única y exclusivamente por los administradores. 
Los magos miembros del grupo pueden emplearlos y hacer que el bot responda con los reales decretos personalizados que hayan creado los administradores del grupo.

Los reales decretos personalizados son una información própia de cada grupo, es por ello que los decretos cambiarán según en el grupo en el que te encuentres.

Pasos para crear decretos:

Para crear un real decreto personalizado se debe escribir "nuevo decreto".

Seguidamente el bot te preguntará qué nombre quieres ponerle a dicho decreto a lo que deberás responder únicamente con el nombre que quieras que tenga (máximo 30 carácteres). Ten en cuenta que cada vez que el bot lea ese decreto responderá automáticamente con la respuesta que le vas a dar. 
Una vez le digas el nombre del comando el bot te pedirá la respuesta que quieres que dé.
Aquí es cuando puedes escribir una frase, poner un gif, un link, un audio, una nota de voz, un video, un fichero o una imagen.

Para solicitar el listado de reales decretos personalizados de un grupo debes escribir en dicho grupo la frase: Listado de decretos. 
La lista de decretos será mandada al privado que tienes con del bot y podrás ver todos los decretos personalizados que tiene ese grupo en concreto.

Por ejemplo, podría haber un decreto personalizado que se llame "ojoloco" y que el bot responderá a este con un gif sobre ojoloco.

Ten en cuenta que el bot responderá únicamente si la frase que se escribas es el decreto personalizado, sin importar las mayúsculas o minúsculas, y borrará el decreto personalizado dejando únicamente su respuesta.

Si deseas borrar un decreto puedes hacerlo con "eliminar decreto {número del decreto}", substituyendo la variable {número del decreto} por el número del real decreto personalizado que tenga en el “Listado de decretos”. Por ejemplo:

Eliminar decreto 55 

En este caso el decreto que se borraría sería el que corresponda al número 55.

Si al intentar borrar un real decreto personalizado el bot te responde que este no existe te recomiendo que le solicites al bot el listado (está explicado más arriba) para que te asegures de cual quieres eliminar.

Para borrar todos los reales decretos personalizados de golpe se puede hacer mediante el comando "eliminar todos los decretos", pero tener cuidado que si el bot tenía en uno de ellos alguna información que querías conservar esta se perderá.

Si en vez de borrar un decreto lo que se quiere es únicamente modificar la respuesta del bot, entonces bastará con crear de nuevo un decreto con el mismo nombre.



4.Listas

Dumbledore dispone de la opción para hacer listas, para quedadas, luchar en fortalezas... Hasta conocer bien es funcionamiento del juego nos servirá para unirnos a vivir esta aventura.
En estas listas únicamente se podrá decir si vas (“Me apunto!”) o si al estar apuntado has decidido no ir (“Paso…”).

Para crear una lista se debe emplear el comando /listamagica y añadir el título que tendrá la lista. Por ejemplo:

/Listamagica quedada viernes

Los entrenadores que se apunten a dicha lista aparecerán junto a la siguiente información: Casa, nivel y Alias de Telegram. 

Con el comando /listareflota puedes reflotar una lista si esta ha quedado hundida. Para ello será necesario que un administrador cite la lista y escriba el comando.

También se dispone de la posibilidad de cerrar una lista para que nadie más se pueda apuntar o desapuntar a partir de ese momento. Esto es posible hacerlo con el comando /listacerrar. Al cerrar la lista los botones para apuntarse y desapuntarse desaparecerán. Para abrir de nuevo una lista cerrada será necesario utilizar el comando /listaabrir; los botones volverán a aparecer y los usuarios podrán volverse a apuntar y desapuntar.

Si se quiere borrar una lista bastará con eliminar el mensaje que sea la lista.


5. Listado de grupos:

Si quieres conocer los grupos de España puedes acudir a:
@mapadelmerodeador

Y si quieres añadir o editar el tuyo del listado:
@merodeadorescharla

En el futuro se espera que el bot disponga de un comando con el cual mandará, a la conversación privada con el bot, la botonera del canal Grupos Wizards Unite del Mapa del Merodeador. 

Al clicar sobre el boton se abrirá el canal Grupos Mapa del Merodeador y podrás ver los grupos que estén dentro 

6. Grupos vinculados.

Será uno de los comandos más útiles del bot, /groups permitirá ver el link de todos los grupos vinculados a un grupo de administración. Por lo tanto, si te encuentras en un grupo de Gryffindor, por ejemplo, y quieres saber el de la ciudad o el de juegos, con utilizar en dicho grupo el comando /groups el bot te mandará al privado una lista de los grupos vinculados, su nombre y el link.

Si eres administrador puedes agregar el link de cada grupo vinculado mediante el comando /add_url seguido de un espacio y el link o alias de este. Por ejemplo: /add_url t.me o /add_url @public_alias.

Para eliminar un link del grupo vinculado y que no aparezca al emplear el comando /groups se deberá escribir /add_url -

Para crear un grupo de administración que tenga uno o diversos grupos vinculados se debe seguir los siguientes pasos:

Ejecutar el comando /create_admin en el grupo al cual quieres que vaya la información, el que será el grupo de Admins. 

Escribe, en el grupo de administración (el grupo de admins) el comando /settings_admin. Este comando te permitirá activar distintas opciones de avisos que llegarán al grupo de Administración, (todo está explicado en ajustes del grupo de Administración). No te preocupes mucho si no sabes bien bien qué activar, dispondrás siempre de este comando y podrás activar o desactivar las opciones siempre que lo necesites recurriendo a ese comando.

6. Añadir el bot a un grupo o canal.

El soporte del bot, por el momento, solo está probado en grupos y supergrupos. En un futuro, contará con soporte en canales.

En grupos el bot ya se puede utilizar tan pronto entra al grupo y envía un saludo. Conviene configurarlo, no obstante. Ten cuidado porque, si una vez añadas el bot conviertes el grupo a supergrupo, tendrás que volver a configurarlo. Un supergrupo es la mejor opción en la mayoría de los casos.

Para añadir el bot a un grupo puedes añadirlo como un contacto más desde el grupo con su alias @ProfesorDumbledorebot.


7. Ajustes del grupo de Administración.

Si bien hemos explicado como configurar un grupo como "admins" y vincular otros grupos, debéis conocer las opciones de las que se dispone

Opciones de las que dispones:

Aviso de la gente que entra al grupo o grupos vinculados.

Aviso cuando se escribe @admin en el grupo o grupos vinculados.

Aviso de expulsiones y baneos individuales en el grupo o grupos vinculados.

Aviso de los warn en el grupo o los grupos vinculados.

Vincular grupos al grupo de Admins


Es importante guardar el ID que te dará el bot, lo necesitarás más adelante. Como ejemplo, a nosotros nos daría:

ID -123456. 

Seguidamente ve al grupo que quieres vincular y ejecuta en dicho grupo el comando /create_link ID. En nuestro caso de muestra sería:

/create_link -123456. 

Vuelve al grupo de administradores e indica, en la botonera, de qué trata el grupo que acabas de vincular. Las opciones de las que dispones son las siguientes:

Icono - Nombre

❤️🦁 Gryffindor
💙🦅 Ravenclaw
💚🐍 Slytherin
💛🦡 Hufflepuff
🗣👥 Grupo de charla
🎮🎲 Grupo de juegos

Para vincular más de un grupo a un mismo grupo de administradores vuelve al paso número 6 (la ID será la misma del paso número 1).

Si quieres que el bot deje de considerar un grupo como grupo de administración puedes hacerlo escribiendo /rm_admin en dicho grupo. Con ese comando se desvincularán todos los grupos que tuvieses vinculados. Si sólo quieres desvincular un grupo entonces dirígete a ese grupo y ejecuta el comando /rm_link.

Para saber qué grupos están vinculados a un grupo de administración escribe el comando /groups y el bot te hará una lista de los grupos vinculados, excepto el de administración.

Configuración básica:

Para hacer la configuración básica del bot utiliza el comando /settings. Este comando se utiliza en el grupo que quieras configurar. La configuración está dividida en varios apartados y subapartados:

8. Ajustes generales (Configuraciones básicas de juegos y modo de administración.)

Quotes: Actualmente esta opción no está disponible.

Juegos:
Quién es
Trivial
Ranas de chocolate
Grajeas

Actualmente estas opciones no están disponibles

Tipo de expulsión por Warns

Respuestas

Límite de Warns

Ajustes de entrada (Configuración de los tipos de grupo y los requisitos.)

Configurar ajustes de entrada

Expulsiones silenciosas o notificadas

Borrar entradas

Tipo de grupo

Ajustes de administración (Configuración de las notificaciones en el grupo de administración)

Aviso admins

Entrada de usuarios

Salida de usuarios

Expulsiones masivas

Expulsiones individuales

Noticias

Canales de Noticias Oficiales

Canales de Noticias No-Oficiales

Bienvenida

Bienvenida

Modo director

Activa o desactiva los chistes, refranes y cualquier cosa que pueda hacer que el bot hable sin que nadie lo invoque. Opción desactivada por defecto.

Juegos

Actualmente esta opción no está disponible.

Activa o desactiva los juegos del bot. Por defecto esta opción está desactivada.

Tipo de expulsión por Warns

Este botón puede estar activado como Ban (Warns) o como Kick (Warns) y determina el tipo de expulsión que recibirá el usuario al llegar al máximo de Warns determinado por el grupo.

Límite de Warns 

Clicando sobre el botón determina la cantidad máxima de Warns que podrá tener un usuario antes de recibir la expulsión del grupo. La cantidad de Warns que se puede configurar es de: 3, 5, 10, 25, 50 o 100.


Noticias

El bot dispone de la opción de Noticias: Eso quiere decir que puede reenviar automáticamente las publicaciones que salgan en distintos canales:

@profesordumbledore
@diarioelprofeta
@ejercitodedumbledore

Cada uno de los siguientes canales tienen sus própias características por los cuales son importantes y seguidos: algunos son de noticias sobre bots, noticias sobre el juego o noticias de broma.

Es decisión de cada grupo activar o no el reenvio de las noticias (y cuales) para mantenerse informados. Por defecto todas las noticias estarán desactivadas. Para activarlas se debe clickar encima del botón y cuando ponga delante el icono ✅, si pone el icono ▪️ quiere decir que esas noticias estarán desactivadas y no serán enviadas al grupo.


Bienvenida

El bot puede dar la bienvenida a los entrenadores que vayan entrando al grupo. Opción desactivada por defecto.

Para activar la Bienvenida es necesario activarla en /settings ✅ (clickando sobre el botón) y después es necesario utilizar el comando /set_welcomepara definir el mensaje de bienvenida que dará el bot. Por ejemplo, si se quiere poner el mensaje “Bienvenidos al grupo”, sería:

/set_welcome Bienvenidos al grupo. 

Además el bot dispone de tres strings que se pueden introducir en el texto de bienvenida para conocer más información del entrenador que acaba de entrar. Por ejemplo:

Strings - Texto mostrado - explicacion

{hpwu} - Luna L60 💙🦅 - Nick + Nivel + Equipo
{Mago} - Luna - Nick
{title} - Ravenclaw España - Nombre del grupo
{id} - 123456789 - ID de Telegram
{nombre} - Lunatica - Nombre en Telegram
{apellido} - Lovegood - apellido en Telegram
{mention} @lunalovegood - Alias de Telegram


Para poner links en el mensaje de bienvenida lo puedes hacer mediante el siguiente string: [NombreLink](Link). Por ejemplo: [ProfesorDumbledore](https://webprofesordumbledore.com).
 Este link que veremos en el mensaje de bienvenida como superdumbledore al clickarlo nos mandará a la web https://webprofesordumbledore.com.

Para escribir texto en negrita dentro del mensaje de bienvenida se debe escribir con un * antes y después del texto, para escribir en cursiva se debe escribir, antes y después del texto, un _ .

Si se quiere eliminar el mensaje de bienvenida, para que el bot deje de saludar cuando entren entrenadores nuevos, entonces se debe escribir el comando /set_welcome sin ningún texto más. También se puede hacer que el bot deje de dar la bienvenida desactivando la opción en /settings.

Para configurar la duración del mensaje de bienvenida se debe emplear el comando /set_cooldown seguido de un número entero y positivo que indicará la cantidad de segundos antes de que sea eliminado el mensaje. Por ejemplo: set_cooldown 15 En este ejemplo el bot mandaría el mensaje de bienvenida cuando entrase un entrenador al grupo, dejaría el mensaje durante 15 segundos y una vez terminada ese tiempo el mensaje del bot se borraría.

Si se quiere desactivar esa opción y que el mensaje no sea eliminado entonces se deberá escribir /set_cooldown 0.

Modo director:

El modo director evita que la gente hable en un grupo, borrando todos los mensajes que pongan los usuarios (no los mensajes de los administradores ni de los bots). Opción desactivada por defecto.

Con el comando /set_nannypuedes definir el mensaje que dará el bot cada vez que un usuario hable. Por ejemplo: */set_nanny Entrenador, para hablar debes ir a @harrypotterwizardsunitespain

Dentro del /settings del apartado del modo director encontrarás una gran cantidad de botones que puedes activar (✅). Si se activan serán los formatos que el bot no permitirá en el grupo.

Por lo tanto, si se activa el modo director el bot no permitirá que los usuarios (no incluye a los bots y administradores) manden mensajes de texto al grupo.

Los formatos siguientes pueden ser bloqueados por el bot: Audio y Voz, Comandos, Contactos, GIFs y Documentos, Imagenes, Juegos, Mensajes, Stickers, Ubicaciones, URLs, Video y Warns.

Finalmente, también hay la opción de activar el botón Mensajes de administradores. Al activar esta opción el bot actuará también sobre los administradores con el modo enfermera.

9. Botones y más botones:

El bot también puede tener botones en el mensaje de bienvenida y en los comandos personalizados, ara ello se debe escribir de la siguiente manera: [Texto a mostrar en el botón](buttonurl://dirección.com). Se debe escribir todo junto, sin espacios (entre los : y las // NO debe de haber espacio), y cambiar el texto del botón y el enlace. Como ejemplo:

[Enlace a google.es](buttonurl://google.es) 

Para escribir más de un botón en una misma línea se ha de escribir :same al final de la dirección. En el siguiente ejemplo se verían 3 botones seguidos (Botón 1, 2 y 3) y en la siguiente línea dos botones (Botón 4 y 5).

[Botón 1](buttonurl://google.es) [Botón 2](buttonurl://google.es:same) [Botón 3](buttonurl://google.es:same) [Botón 4](buttonurl://google.es) [Botón 5](buttonurl://google.es:same)* 

10. Normas del grupo Admins

El bot puede guardar y enviar las normas del grupo por privado.

Para registrar las normas del grupo se debe escribir el comando /set_rules seguido del texto que se quiera

guardar como normas. Una vez enviado el bot responderá que se han establecido correctamente las normas del grupo.

El comando /set_rules acepta únicamente el formato texto. También es posible añadir botones.
El comando /rules hará que el bot responda por privado con el mensaje que se haya guardado como las normas del grupo.

Si un usuario entra nuevo al grupo cuando están las normas activas entonces deberán clicar sobre el botón Normas que aparecerá en la bienvenida y luego en el privado del bot en /start para poder hablar en el grupo. No se recomienda tener activas las normas del grupo mientras a la vez que el /set_cooldown de la bienvenida.

Para eliminar las normas del grupo será necesario escribir en el grupo /clear_rules.

Cosas a tener en cuenta:

No es recomendable tener las Normas del grupoactivas junto a la Bienvenida con /set_cooldown. Si se activan las dos cosas es recomendable hacer un Comando personalizado en el cual puedan encontrar el botón con las Normas del grupo. Para más información leer Comandos personalizados).

Zona horaria ⤴

El bot reconoce la hora que escriben los usuarios y hace operaciones con ellas, por lo que es importante que la hora que utilice el bot se corresponda con la hora real de tu grupo.

Para establecer la zona horaria correcta se debe utilizar el comando /set_timezone con la zona horaria correspondiente como parámetro siguiendo el formato del listado de zonas horarias de la IANA. Por ejemplo:

/set_timezone Europe/Madrid /set_timezone Atlantic/Canary

11. Gestión de usuarios

Para saber la cantidad de magos de cada casa que hay en un grupo y saber los magos que no están validados, puedes emplear el comando /dumbleuv y el bot te mostrará un mensaje parecido a este:

💙 Ravenclaw: 10

💛 Hufflepuff: 3

❤️ Gryffindor: 8

💚 Slytherin: 3

🖤 No Validados: 5

(?) Desconocidos: 12

Los nicks de los magos de uno de los equipos se pueden ver mediante:

💙 Ravenclaw -> /dubleuv R

💛 Hufflepuff  -> /dubleuv H

❤️ Gryffindor ->  /dubleuv G

💚 Slytherin ->  /dubleuv S

No Validados ->  /dubleuv 

Para que muestre una lista con todos -> /dumbleuv all

El comando /dumblekickuv sirve para expulsar a todos aquellos No Validados en el bot. El bot no puede expulsar a los que no conoce, pero si a los que no están validados y conoce.

Cosas a tener en cuenta:

AVISO: antes de usar el comando /doblekickuv ten en cuenta que el único bot validado con @dumbledorebot es el própio bot @dumbledorebot.

El comando /dumblekickuv y /dubleuv, ambos con sus variantes, está restringido a una vez al día por grupo (independientemente de si este está vinculado o no). A las 00.00 se reinicia y se puede volver a utilizar.

12. Id:

Saber el Id de un mago es posible gracias al comando /id. Este comando no és exclusivo para administradores, pero está orientado y pensado principalmente para a estos.

El comando, al igual que el "informe", se puede emplear como:

Citando un mensaje del mago.

Citando un reenviado de un mensaje del mago.

Con el nick del mago.

Con el alias de Telegram del mago (Importante: sin el @).

La respuesta será enviada al privado del bot y el comando será borrado (siempre que el bot tenga los permisos necesarios).

Ejemplo de respuesta enviado al privado al emplear el comando /id sobre un mago:

ID: 123456789 Alias: @luna Nick: lunatica Nivel: 60 Casa: Ravenclaw 



13. Otros comandos exclusivos para administradores:

Algunos de los comandos más importantes para un administrador son los de tipo “castigo”. Estos comandos únicamente pueden ser utilizados por los administradores, y si algún usuario lo escribiese el bot respondería que dicho usuario no tiene permisos para ello.

En los comandos exclusivos para administradores de tipo “castigo” hay de dos tipos:

Comandos de expulsiones individuales: un comando “castigará” a un solo usuario.

Comandos de expulsiones masivas: un comando “castigará” a varios solo usuarios.

Comandos de expulsiones individuales ⤴

La mayoría de bots disponen de tres “castigos” muy diferenciados: Warn, Kick y Ban.

/warn - El Warn es un aviso (advertencia), que después

de una determinada cantidad de avisos será una expulsión del grupo por kick o ban (dependiendo de cómo esté configurado). Para ver la configuración de los Warn lee el apartado Tipo de expulsión por Warns y Cantidad de Warns.

/kick - El Kick es la expulsión del grupo a un usuario, pero este podrá volver a entrar al momento.

/ban - El Ban es la expulsión del grupo a un usuario, y este no podrá volver a entrar al grupo hasta que un administrador le quite el ban.

Para utilizar alguno de estos tres comandos se puede hacer mediante las siguientes opciones:

Citando el mensaje del usuario al que se quiere “castigar” y escribiendo el comando.

Escribiendo el comando seguido del nick de mago del usuario. Por ejemplo: /ban Lunatica

Escribiendo el comando seguido del alias de Telegram del usuario. Por ejemplo: /kick lunalovegood

Escribiendo el comando seguido del ID del usuario. Por ejemplo: /warn 111111 Para conseguir el ID del usuario se puede hacer mediante el aviso del bot en el grupo de administración, si se tiene activado (para saber más información leer el apartado Ajustes de administración), o mediante el comando /id (para más información leer el apartado Id).

Los tres comandos permiten además, con todas sus opciones, añadir un mensaje con el motivo de dicho “castigo”. Por ejemplo: /kick lunatica por no asistir a la clase de pociones. 

También es posible, si se hace desde el grupo de administración, especificar en qué grupo será el “castigo” mediante el ID del grupo. Por ejemplo: /ban -19999999 lunatica. En este ejemplo se haría un ban desde el grupo de administración en el grupo con ID -19999999 y al usuario con el nick de entrenador lunatica.

Comandos de expulsiones masivas ⤴

En proceso de escritura

/Dumblekickold {X} - Siendo {X} el número de días que llevan los usuarios sin mandar mensajes. Por ejemplo:

/Dumblekickold 30

Serian expulsados los magos que llevan 30 días sin hablar.

/Dumblekickmsg {X} - Siendo {X} el número de mensajes que deben haber enviado los usuarios al grupo. Ejemplo:

/Dumblekickmsg 50 

Todos los magos que no hayan enviado 50 mensajes serán expulsados.

/Dumblekicklvl {X} - Siendo {X} el nivel que tiene que tener el usuario para no ser expulsado. Ejemplo:

/dumblekicklvl 15 

Todos los que estén por debajo de 15 serán expulsados del grupo.

14. Glosario de comandos para administradores ⤴

En proceso de escritura

Comando - Descripción 
/settings_admin - Ajustes del grupo de Admins
/create_admin - Vincular grupos al grupo de Admins
/create_link - Vincular grupos al grupo de Admins
/rm_admin - Vincular grupos al grupo de Admins
/rm_link - Vincular grupos al grupo de Admins
/settings - Configuración básica
/set_welcome - Bienvenida
/set_cooldown - Bienvenida
/set_nanny - Bienvenida
/set_zone - Zona horaria
/Dumbleuv - Gestión de usuarios
/Dumblekickuv - Gestión de usuarios
/id - Id
nuevo decreto - Comandos personalizados
Listado de decretos - Comandos personalizados
eliminar decreto {número de decreto} - Comandos personalizados
eliminar todos los decretos - Comandos personalizados
/ban - Comandos de expulsiones individuales
/kick - Comandos de expulsiones individuales
/warn - Comandos de expulsiones individuales
/Dumblebanuv 
/Dumblebanmsg - Comandos de expulsiones masivas
/Dumblebanold - Comandos de expulsiones masivas
/Dumblebanall 
/Dumblebanteam
/Dumblebangroup
/unban
/Dumblekickuv
/Dumblekickmsg 
/Dumblekickold 
/Dumblekickall 
/Dumblekickteam
/Dumblekickgroup 
/Dumblekickeveryone 
/Dumblewarnuv 
/Dumblewarnmsg
/Dumblewarnold 
/Dumblewarnall 
/Dumblewarngroup 
/mk_admin 
/add_group
/add_link
/rm_group
/request_verification
/groups 


#3
#3
#3


/start - iniciar bot
/cucuruchodecucarachas - Registrarse en el bot
/miperfil - profile
/informe - quien es?
/informe {Entrenador} - Quién es
/Tabla (hechizos, varitas...) - Tablas
Listado de decretos - Listado de comandos
Crear decreto - crear comando

/listamagica - Listas
/Reflotalista - reflota listas
/Cerrarlista - cerrar lista 
/Abrirlista - abrir lista 

/groups - Grupos vinculados

1. Cuando la gente ponga /start al bot:

Usuario: /start

Joy: 📖 ¡Bienvenido al centro Pokémon de la Enfermera Joy! Tómate tu tiempo en leer la guía de entrenadores.

Lee con detenimiento la politica de privacidad antes de registrarte.

💙💛❤️Registrar nivel/equipo
Escríbeme por privado en @NurseJoyBot el comando /register. En vez de eso, puedes preguntar /profile a @detectivepikachubot y reenviarme su respuesta.

🔔 Subida de nivel
Para subir de nivel, unicamente debes enviarme una captura de pantalla de tu perfilde Pokémon GO por privado y yo haré el resto." 

Dumbledore: Bienvenido al mundo mágico, para registrarte conmigo debes entrar en mi despacho, escribeme por privado la contraseña /cucuruchodecucarachas 

Son nuestras elecciones las que muestran lo que somos, mucho más que nuestras habilidades, así pues elige bien y dime, ¿Cual es tu casa de hogwarts? 

(Botones)" 

-------

2. Cuando añadan al bot a un grupo:

Joy: "Entrenadores de Pruebas, sed bienvenidos al Centro Pokémon de la región de Telegram.
Antes de poder utilizarme, un administrador tiene que configurar algunas cosas. Comenzad viendo la ayuda con el comando /help para conocer todas las funciones. Aseguraos de ver la ayuda para administradores, donde se explica en detalle todos los pasos que se deben seguir."


Dumbledore: "Primero debes decirme en que idioma quieres que hable.



Antes de comenzar nuestra aventura, quiero decir unas pocas palabras, _papanatas, llorones, baratijas, pellizco._

/kick :

👌 Mag@ Nelulita expulsad@ correctamente de la clase!

/Ban:

👌 Mag@ Nelulita banead@ correctamente del castillo!

/Warn:

Mag@ Nelulita advertid@ implica perdida de puntos a su casa! 1/50