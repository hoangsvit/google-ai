# ePlus AI Toolkit — Español

<!-- Source README.md git-blob: 4f68b0ea54146c62a96a97b322a6c8cab816547e -->

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Español** · [Français](README.fr.md)

**Vista previa de macOS:** la [versión para Mac](docs/MACOS-PREVIEW.md) implementa los pasos 0–5. Los pasos de pago 2–5 pueden generar cargos reales y requieren confirmación individual; el funcionamiento real con Mac/MuMu aún no se ha verificado.

> **Documento de referencia:** [README original en inglés](README.md). Esta versión está redactada en español para que resulte más fácil de seguir, sin cambiar las instrucciones técnicas ni las advertencias. Si encuentras alguna diferencia, consulta el código y la documentación original.

**ePlus AI Toolkit** permite consultar las ofertas de Google AI Pro disponibles a través de Google One y Google Play en un dispositivo Android. Funciona en **Windows y macOS**: en Windows se inicia desde PowerShell y en Mac desde Terminal (zsh/bash). Tanto la interfaz Textual como los comandos de terminal utilizan el mismo motor basado en Python, ADB y Frida.

![Interfaz de ePlus AI Toolkit](images/terminal-ui-overview.png)

> [!CAUTION]
> **Proyecto no oficial; pueden producirse cargos reales.** Los **pasos 2–5** pueden abrir un proceso de pago real de Google Play y pulsar **Subscribe** automáticamente. Encontrar una oferta, ver un precio inicial de cero o recibir un mensaje de envío del pago **no demuestra** que la cuenta cumpla los requisitos, que la suscripción sea gratuita, que esté activa ni que se haya ampliado. Antes de cada pago, comprueba en Google Play la cuenta, el importe de hoy, el precio de renovación y la siguiente fecha de cobro. Detener el programa no deshace una transacción enviada.

> [!NOTE]
> **Ten al menos 3 USD disponibles para tres operaciones separadas de 1 USD; no es un único cargo de 3 USD.** En el caso comunicado de **24 meses**, el paso 2 (12 meses iniciales), el paso 3 (+6 meses) y el paso 4 (+6 meses) corresponden a **tres operaciones de verificación de tarjeta o pago de 1 USD cada una**: **3 × US$1 = US$3**. Una operación puede ser una retención temporal de autorización y no un cargo definitivo; Google Play o el banco pueden aplicar importes distintos. **Los 3 USD son el saldo mínimo del ejemplo, no una tarifa fija ni una garantía de que cualquier cuenta obtenga los 24 meses.** Las preautorizaciones pueden reducir el saldo disponible y suelen liberarse en **1–14 días laborables**, según el banco. Comprueba tras cada paso la operación y la fecha de renovación en Google Play. El paso 5 es opcional y **no forma parte de estas tres operaciones**. [Información oficial de Google Play](https://support.google.com/googleplay/answer/6224192?hl=en).

## Descargo de responsabilidad

Este proyecto es **independiente y no está afiliado, patrocinado ni respaldado** por Google, Google One, Google Play, NetEase o MuMuPlayer. El software se ofrece **tal cual**, sin garantías de elegibilidad, resultado de suscripción o compatibilidad. Úsalo solo con cuentas y dispositivos propios o autorizados y respeta las leyes y condiciones de cada plataforma. Lee el [descargo completo (inglés)](DISCLAIMER.md) y las [precauciones de seguridad](SECURITY.md).

## 1. Preparar el entorno

**Sigue las instrucciones de tu sistema operativo.** En macOS no hace falta instalar PowerShell.

| Componente | Windows | macOS |
| --- | --- | --- |
| Terminal | **PowerShell 5.1 o posterior** | **Terminal**, con zsh o bash |
| Python | **3.10 o posterior** (comando `python`) | **3.10 o posterior** (`python3`); se crea un entorno `.venv` local |
| Git | Git para Windows | Git mediante Xcode Command Line Tools o Homebrew |
| Android | Dispositivo o emulador con root y ADB; el proyecto contempla **MuMuPlayer para Windows** | Dispositivo Android con root o emulador compatible; **MuMuPlayer Pro para Mac** es una opción para equipos Apple Silicon, no para Intel |
| Aplicaciones | Google Play Store y Google One, con la cuenta que quieres comprobar | Las mismas aplicaciones en el Android elegido |
| ADB | El programa puede localizar o descargar Android SDK Platform-Tools | Debes instalarlo por separado, por ejemplo, con `brew install android-platform-tools`; compruébalo con `adb devices` |
| Frida | **16.5.9**; la preparación de Windows puede configurarla | **16.5.9** en `.venv`; es necesario comprobar que sea compatible con Android |
| Inicio | `.\run-all.ps1` | `sh run-macos.sh` o `ePlus-AI-Toolkit.command` |

En ambos sistemas necesitas acceso autorizado a un entorno Android correctamente configurado. Aunque la implementación de macOS incluye los pasos 0–5, **no se ha probado un proceso de pago real en Mac/MuMu**. Consulta las guías de [Windows](docs/INSTALLATION.md) y [macOS](docs/MACOS-PREVIEW.md).

### Requisitos en Windows

- Windows con **PowerShell 5.1 o posterior** y **Python 3.10 o posterior**.
- MuMuPlayer instalado por tu cuenta, con root y depuración ADB activados.
- Google Play Store y Google One instalados y conectados a la cuenta que quieres consultar.
- Una conexión ADB y una versión de **Frida 16.5.9** compatible. La herramienta puede ayudarte a preparar estos componentes, pero **no instala MuMuPlayer**.

### Paso 1 — Instalar MuMuPlayer

Descarga la edición para Windows desde la [web oficial de MuMuPlayer (NetEase)](https://www.mumuplayer.com/download/). Evita los sitios de descargas no oficiales.

Inicia el emulador, activa root y ADB y verifica que Google Play Store y Google One estén disponibles. Después, inicia sesión en la cuenta de Google que vas a comprobar.

También puedes consultar la [guía ilustrada de instalación en GitHub Wiki](https://github.com/hoangsvit/google-ai/wiki/Install).

## 2. Descargar y ejecutar

En PowerShell:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

Si ya clonaste el repositorio:

```powershell
git pull --ff-only
.\run-all.ps1
```

Al ejecutar **sin parámetros** se abre el panel Textual; no se inicia una compra automáticamente. Cuando sea necesario, el programa puede preparar Textual, ADB o Frida. Normalmente **no hace falta** ejecutar `setup_env.py` antes. La preparación puede modificar el emulador, el proxy o la configuración de red.

Si ADB está disponible en PATH, comprueba la conexión:

```powershell
adb devices
```

El estado debe ser `device`, no `offline` ni `unauthorized`. Más información en la [guía técnica](docs/DETAILED-GUIDE.md).

### Si la versión más reciente no funciona, prueba una versión publicada

Si la versión más reciente del repositorio falla, puedes probar **una versión publicada anteriormente** en [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Lee las notas y descarga el paquete de Windows **si está adjunto**. Si únicamente aparece el archivo automático **Source code (zip)** de GitHub, descárgalo, descomprímelo, abre PowerShell en la carpeta extraída y ejecuta:

```powershell
.\run-all.ps1
```

**Source code (zip) no es un `.exe` precompilado ni un instalador.** Guarda la versión publicada en **otra carpeta**, sin sobrescribir tu copia actual. Una versión anterior puede no contener las correcciones más recientes; siguen siendo necesarios Windows, Python, MuMuPlayer, ADB/Frida y las mismas precauciones sobre pagos. Si el problema continúa, consulta la [guía de solución de problemas](docs/DETAILED-GUIDE.md) o [abre una incidencia](https://github.com/hoangsvit/google-ai/issues).

## macOS — Instalación y ejecución

En macOS, instala **Git**, **Python 3.10+** y **Android SDK Platform-Tools (ADB)** (Homebrew: `brew install android-platform-tools`). Conecta un dispositivo Android con root, Google Play Store y Google One, o un emulador compatible. **MuMuPlayer Pro para Mac requiere Apple Silicon**; en Intel se necesita otro entorno Android compatible.

Abre **Terminal** y ejecuta:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

`sh run-macos.sh` abre el panel Textual con **pasos 0–5**. `--check` revisa el entorno (puede modificar ajustes), `--list` solo consulta ofertas y `--step 2` solo selecciona el paso, **sin pagar automáticamente**. Los pasos 2–5 pueden generar cargos reales y requieren aprobación individual. **Los pagos en un Mac/MuMu real aún no se han verificado.** Consulta la [guía Mac completa](docs/MACOS-PREVIEW.md).

## Linux — Instalación y ejecución

En Ubuntu x86_64, instala Git, Python 3.10 o posterior con `venv` y `pip`, y Android SDK Platform-Tools. Agrega `adb` a `PATH` o indica la ruta del ejecutable en `ADB_PATH`. Conecta por USB un teléfono Android con acceso root, Google Play Store y Google One. Activa la depuración USB, desbloquea el teléfono y autoriza la conexión. Comprueba que ADB muestre un solo dispositivo con estado `device`.

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git switch feature
adb devices
sh run-linux.sh
```

Usa una versión que incluya `run-linux.sh`. El script abre el panel e instala las versiones fijadas de Textual y Frida 16.5.9 en un entorno local `.venv`. Si Ubuntu no puede crearlo, instala `python3-venv` o el paquete venv de tu versión de Python.

- `sh run-linux.sh --check` ejecuta el paso 0 y puede modificar ajustes de Android, Frida o la red.
- `sh run-linux.sh --list` ejecuta el paso 1 y lista las ofertas sin iniciar el pago, aunque puede preparar el entorno de Android.
- `sh run-linux.sh --step 3` abre los controles avanzados con el paso 3 seleccionado. `sh run-linux.sh --sequence` abre los controles guiados desde el paso 2. Ninguno inicia un paso automáticamente.

**Android 16 y versiones posteriores.** El script de Linux se detiene antes de configurar el dispositivo porque Frida 16.5.9 es anterior a la compatibilidad con Android 16. Puedes comprobar la conexión USB con **Diagnose Android connection**.

**Los pasos 2–5 pueden generar cargos reales en Google Play.** Cada uno requiere su propia aprobación, la verificación de la cuenta de Play activa y una consulta reciente que identifique exactamente la oferta con un primer período de precio cero. Antes de avanzar, verifica la suscripción y la fecha de renovación en Google Play. Los pagos en Linux se comprueban con simulaciones. Sigue pendiente la validación completa en un dispositivo real. [Instalación en Linux, solución de problemas de USB y verificación](docs/LINUX.md).


## 3. Usar el panel Textual

Mientras se ejecuta un paso, se desactivan **Check Device & Offers**, **Run** y los controles para cambiar de modo o de paso, de modo que no se inicien varias acciones a la vez. El paso 0 puede cambiar ajustes del equipo y el paso 1, aunque no realiza compras, puede preparar ADB/Frida. Antes de continuar con **Next**, comprueba el resultado en Google Play. **Detener o cerrar la aplicación no anula un pago ya enviado.**


**Check Device & Offers** ejecuta **Step 1 — Available offers**: consulta ofertas y **no inicia el pago**. Supervisa **Live Status** y **Show technical details**; 30 segundos sin nuevos mensajes no implican necesariamente un bloqueo.

Mientras la interfaz está inactiva, la herramienta comprueba las conexiones ADB existentes aproximadamente cada cinco segundos. Si no encuentra ADB o el dispositivo Android, muestra una ventana con indicaciones. Sigue comprobando y actualiza el estado del dispositivo; reconectarlo no desbloquea por sí solo los pasos de pago. La supervisión se pausa durante un paso o mientras hay otros diálogos abiertos. No instala ni conecta dispositivos en segundo plano, aunque `adb devices` puede iniciar el servidor ADB local.

En Windows, al ejecutar **Check Device & Offers**, la herramienta busca ADB y, si hace falta, intenta descargar Android SDK Platform-Tools oficial. La descarga o instalación puede fallar; consulta **Show technical details** si ocurre. En macOS, instala Platform-Tools siguiendo las instrucciones para Mac. Instala e inicia MuMu por separado, activa root y la depuración ADB e inicia sesión en Google Play y Google One.

Los pasos 2–5 solo se desbloquean cuando una nueva comprobación del paso 1 devuelve ofertas y verifica la cuenta de Play. Si la oferta de 12 meses `12months-eft` tiene una primera fase de precio 0, la ventana de resultado y la pantalla principal muestran **Continue to Step 2**; de lo contrario, revisa la lista. Este botón abre una confirmación independiente y no garantiza la elegibilidad ni el coste final. Tras solicitar el pago, comprueba la suscripción, la fecha de renovación y los cargos reales en Google Play antes de elegir **Verified in Google Play → Next**. Cada paso posterior requiere una confirmación propia. Una nueva comprobación, un fallo en un paso de pago o un cambio de dispositivo pueden bloquear de nuevo los pasos de pago.

En **Choose another step**:

De forma predeterminada solo se ejecuta el paso elegido. En **Choose another step**, selecciona **More run options…** al final del menú de pasos para mostrar los modos guiados.

| Modo | Acción |
| --- | --- |
| **Stop after this step** | Ejecuta un único paso seleccionado, del 0 al 5 |
| **Offer the next step** | Inicia una secuencia guiada desde el paso que elijas (entre el 2 y el 5) |
| **Start at Step 2** | Inicia la secuencia desde el paso 2; el 5 es opcional |

| Paso | Función | Riesgo |
| --- | --- | --- |
| **0 — Environment** | Diagnóstico/preparación de Android, ADB y Frida | Sin compra; puede cambiar ajustes locales |
| **1 — Available offers** | Consulta de ofertas de Google Play | Sin compra; la preparación puede cambiar ajustes |
| **2 — Pro 12 months** | Oferta original de 12 meses | **Posible cargo real** |
| **3 — Pro +6 months** | Actualización de suscripción original | **Posible cargo real** |
| **4 — Pro +6 months (second)** | Segunda actualización de suscripción | **Posible cargo real** |
| **5 — Optional +6 months** | Actualización adicional opcional | **Posible cargo real** |

**Ejemplo comunicado de 24 meses (debe confirmarse en Google Play):**

| Paso | Duración si se aplica | Operación independiente |
| --- | --- | --- |
| **2 — Pro 12 months** | **12 meses** iniciales | **1 USD** (primera operación) |
| **3 — Pro +6 months** | **18 meses** en total | **1 USD** (segunda operación) |
| **4 — Pro +6 months (second)** | **24 meses** en total | **1 USD** (tercera operación) |
| **Total hasta el paso 4** | **24 meses, si se confirma** | **3 × US$1 = US$3**; no un pago único de 3 USD |

**El paso 5 es opcional y no se incluye en estas tres operaciones.** El plazo anunciado o una preautorización no demuestran que la ampliación se haya completado: verifica la suscripción y su renovación después de cada paso.

Los meses son **nombres históricos de los pasos**, no una garantía de ampliación. Si ya tienes una suscripción activa, **no repitas el paso 2**.

El TUI exige **aprobación explícita por cada paso de pago**. Aunque aparezca un mensaje de pago enviado, comprueba el estado real, los cargos y la renovación en [Suscripciones de Google Play](https://play.google.com/store/account/subscriptions). Pulsa **Verified in Google Play → Next** solo si has confirmado personalmente el cambio. La herramienta **no puede demostrar por sí misma** la activación.

**Detener/salir:** Stop en los pasos 0–1 solicita cancelar el proceso local. En los pasos 2–5, **Stop after this step** evita los pasos siguientes, pero **no fuerza la interrupción de un pago en curso**. **Q / Exit** espera a que acabe el paso de pago actual. **D** alterna los detalles; **R** inicia el modo seleccionado.

### Dispositivo, cuenta e historial

La tarjeta Device muestra la versión de Android, SDK, ABI y conexión ADB cuando están disponibles; sitúa el puntero encima para ver los datos completos. **Choose account**, junto a Account, enumera las cuentas iniciadas en Android. Selecciona el perfil correcto en Play Store y Google One y repite Step 1. El programa utiliza el correo del perfil activo cuando Play Store lo identifica explícitamente.

El panel de acciones se ajusta a sus controles y **Live Status** ocupa la altura restante, con la actividad más reciente arriba. **Show technical details** abre un registro que sigue las líneas nuevas. El botón principal y **Run this step** muestran el paso en ejecución y los segundos transcurridos. En Windows, Step 0 recibe una marca al terminar la comprobación del entorno dentro de la consulta de ofertas. Si falta una comprobación reciente verificada, aparece **Check Device & Offers — Step 1** en verde.

**Recent history** guarda inicios, resultados y la acción **Verified in Google Play → Next** en `logs/stage-history/`. Al abrir la aplicación se recupera el historial más reciente; al elegir una cuenta se muestra el suyo. **↺** indica un paso intentado anteriormente. El historial no confirma una suscripción ni desbloquea pagos. Tras reiniciar la aplicación o cambiar de cuenta hay que repetir Step 1. Las ejecuciones anteriores a esta función no se pueden recuperar.

El aviso de desconexión incluye **Retry connection**, que muestra **Retrying…** y los segundos; **Got it** cierra el aviso. En Windows se intenta reconectar el emulador local, también al iniciar un paso sin dispositivos ADB conectados. Durante las consultas se intenta reiniciar una vez una aplicación que no arranca. Si falla, cierra MuMu, vuelve a abrirlo, espera a que Android termine de arrancar y repite Step 1. Google One se reinicia antes de consultar; Play Store continúa abierto si ya está disponible. **Reload toolkit** reinicia la interfaz inactiva con el código local y crea una sesión nueva.

Antes de pulsar **Subscribe** automáticamente, la pantalla de pago debe mostrar exactamente el correo esperado, un total de hoy de cero y la duración de prueba prevista; la oferta solicitada también debe coincidir. Si el correo falta o difiere, se detiene la pulsación para permitir una revisión manual. Cada paso de pago requiere aprobación propia. Después del envío, verifica la suscripción, la renovación y los cargos en Google Play. El recordatorio de las tres verificaciones de tarjeta aparece en las aprobaciones de pago.

## 4. Comandos de PowerShell (avanzado)

**Solo para Windows.** Estos comandos utilizan PowerShell; en macOS debes usar `run-macos.sh` y las [instrucciones para Mac](docs/MACOS-PREVIEW.md). Si indicas parámetros, se abre el modo CLI en lugar del panel Textual.

**Consulta y diagnóstico, sin pago:**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**Los siguientes comandos pueden iniciar pagos reales:**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

A diferencia del TUI, un comando individual `-Step 2..5` **no pide una segunda aprobación escrita en PowerShell**. Ejecútalo solo si realmente deseas intentar una compra y ya comprobaste las condiciones.

Secuencia guiada del CLI:

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

Confirmaciones: **1 = Continue (continuar), 2 = End run (terminar), 0 = Stop (detener)**. Comprueba Google Play antes de pasar al paso siguiente. `-StartStep 3` no demuestra que las ampliaciones anteriores hayan funcionado.

Parámetros opcionales:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Usa solo un número de serie mostrado por ADB. Evita `-Force`: omite la comprobación de la cuenta, **pero no modifica** la elegibilidad ni las restricciones de pago de Google.

## 5. Resultados y solución de problemas

- **MuMu/ADB no detectado:** revisa el emulador, root, ADB y los permisos del dispositivo.
- **Error de Frida:** revisa los detalles y la compatibilidad de **16.5.9** con Android.
- **Sin ofertas:** abre Google One/Play Store y vuelve a ejecutar **Step 1**.
- **Cuenta incorrecta:** verifica el perfil de Google Play; no omitas la comprobación.
- **Pago solicitado:** no confirma una suscripción nueva ni una renovación; revisa Google Play antes de repetirlo.
- **Error de seguridad de pagos (por ejemplo OR-REH-04):** detén los pasos de pago y sigue el procedimiento oficial.

Los registros están en `logs/` y los informes en `ultra0-report/`. **No compartas archivos sin ocultar correos, tokens y datos de pago.** Las pruebas automáticas de CI se ejecutan con datos simulados y **no verifican compras reales**. 
## Soporte comunitario y proyectos relacionados

Si tienes problemas para instalar o utilizar ePlus AI Toolkit, puedes contactar e intercambiar consejos con la comunidad en la [publicación de soporte y debate de ePlus en Telegram](https://t.me/eplus_news/29). Para errores reproducibles, también puedes [abrir un Issue en GitHub](https://github.com/hoangsvit/google-ai/issues). **No compartas contraseñas, códigos OTP/2FA, tokens de ofertas o compras, registros sin anonimizar ni datos de tarjetas.** No es un canal de soporte oficial de Google.

**¿No puedes acceder a la oferta de Google AI Pro?** Puedes conocer otro proyecto comunitario de ePlus.DEV: [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub), donde es posible [buscar o compartir códigos de invitación de Muse](https://muse.eplus.dev/). **Muse es un servicio distinto**: sus códigos **no activan ni sustituyen** una suscripción a Google AI Pro. La disponibilidad de los códigos y los requisitos de acceso pueden variar.

## Organización del repositorio

Los scripts de inicio y los módulos Python principales siguen en la carpeta raíz para que las instrucciones existentes continúen funcionando. En Windows, utiliza `run-all.ps1`; en macOS, `run-macos.sh`.

| Archivo o carpeta | Para qué sirve |
| --- | --- |
| `run-all.ps1` | Abre el panel Textual o el modo CLI de Windows |
| `run-macos.sh`, `ePlus-AI-Toolkit.command`, `macos_runner.py` | Inicio y ejecución de los pasos 0–5 en Mac; los pagos reales no se han verificado |
| `tui.py`, `tui_core.py`, `ultra0.py`, `setup_env.py`, `device_selector.py`, `query_sku.py` | Componentes Python que utiliza actualmente la herramienta |
| [`tools/windows/`](tools/windows/README.md) | Configuración manual opcional para Windows |
| [`legacy/windows/`](legacy/windows/README.md) | Archivos .bat antiguos; algunos usan `--force` para omitir la comprobación de cuenta y pueden provocar **cargos reales** |
| `scripts/`, `assets/` | Utilidades y recursos de Android/Frida |
| `tests/`, `.github/workflows/`, `docs/` | Pruebas, GitHub Actions y documentación |

## Documentación y colaboración

[README en inglés](README.md) · [Wiki de instalación](https://github.com/hoangsvit/google-ai/wiki/Install) · [Guía detallada](docs/DETAILED-GUIDE.md) · [Pasos originales](docs/ORIGINAL-STEPS.md) · [Descargo](DISCLAIMER.md) · [Seguridad](SECURITY.md) · [Contribuir](CONTRIBUTING.md) · [Avisos de terceros](THIRD_PARTY_NOTICES.md)

La documentación incluye [estructura del proyecto](docs/PROJECT.md), [uso del panel y CLI](docs/USAGE.md), [seguridad de facturación](docs/SAFETY.md), [notas del autor](docs/AUTHOR-NOTES.md) y [normas para agentes](AGENTS.md). GitHub Actions prueba Python, PowerShell, Textual y Frida/Billing mediante simulaciones, **sin transacciones reales**. Que las pruebas de CI pasen no garantiza la compatibilidad con tu dispositivo ni que tu cuenta cumpla los requisitos.

## Créditos

**Autor original:** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **Mantenedor:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). El aviso MIT del autor original permanece en `THIRD_PARTY_NOTICES.md`.

[Centro de documentación](docs/README.md) · [Guía histórica en español](docs/i18n/README.es.md) · [Seguridad de pagos](docs/SAFETY.md)
