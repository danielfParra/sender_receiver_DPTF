# Protocolo Poyecto Tilman & Daniel 

## 1. Entorno del proyecto


Python del entorno virtual:

`.venv\Scripts\python.exe`

Preparación de sesión PowerShell:

```powershell
Set-Location "c:XXXX\SR_otree-NEW-2026"
$env:Path = "$PWD\.venv\Scripts;" + $env:Path
```

## 3. Checklist de producción (antes de lanzar)

Verificar estos puntos en cada lanzamiento real:

1. `DEBUG` desactivado:
`$env:OTREE_PRODUCTION = "1"`

2. Protección de acceso activada:
`$env:OTREE_AUTH_LEVEL = "STUDY"`

3. Comando de arranque correcto:
`otree prodserver 8000`

## 2. Arranque recomendado de servidor (PowerShell)

```powershell
Set-Location "c:XXXX\SR_otree-NEW-2026"
$env:Path = "$PWD\.venv\Scripts;" + $env:Path
$env:OTREE_PRODUCTION = "1"
$env:OTREE_AUTH_LEVEL = "STUDY"
otree prodserver 8000
```

URL local:

`http://localhost:8000`

## 3. Preparación de la sala de laboratorio

Verifique que todos los computadores estén encendidos y que el navegador tenga la ventana
del experimento cargada.
Una vez estén listos, oprima F11 en cada computador para activar el modo pantalla completa.
Esto evita que los participantes cambien de pestaña o usen otras aplicaciones.

## 4. Dentro del laboratorio

Una vez todos estén sentados y se haya ajustado el número de personas en el programa, leer en voz alta:

"Bienvenidos y bienvenidas nuevamente al laboratorio y muchas gracias por venir.
Por favor recuerden que, a partir de este momento, cualquier tipo de comunicación
está prohibida. Si tienen alguna pregunta, simplemente levanten la mano y nos
acercaremos a ayudarles y responder sus dudas individualmente.
Les solicitamos evitar movimientos bruscos con los pies, ya que podrían apagar
accidentalmente el computador. Por favor no abran otras pestañas ni salgan de la
pestaña del experimento que tendrán en un momento en pantalla."

Durante la sesión:

1. No camine por los pasillos mientras los participantes toman sus decisiones.
2. Quédese junto al computador-servidor en la sala.
3. Monitoree la data en oTree hub.

Si alguien abre una ventana diferente a la convencional, decir:

"Estimados participantes, le recordamos que está prohibido abrir pestañas o aplicaciones distintas a la del estudio."


## 5. Una vez los participantes vayan finalizando

Leer en voz alta:

“Apreciadas personas participantes: Les solicitamos permanecer en sus asientos si aún no han finalizado el formulario de pagos. Si ya lo han completado, les pedimos amablemente que se dirijan al casillero ubicado en la parte posterior de la sala, cerca de la puerta por la que ingresaron. Busquen aquel que corresponde con el número de su llave, retiren su celular y dejen la llave colgada dentro de la rendija del locker.

En caso de tener alguna pregunta o consulta, por favor levanten la mano y con gusto les atenderemos. Les recordamos que pueden llevarse un código QR o escanear el que se encuentra en recepción para invitar a otras personas a participar en este tipo de proyectos.

Asimismo, les recordamos que su pago lo recibirán máximo en tres días hábiles. Allí también se incluirá el bono de la tarea de replicación si se lo ganaron. Agradecemos sinceramente su participación y esperamos verles próximamente.”



