import network
import socket
import time
from machine import Pin, PWM

# Pines
IN1 = Pin(10, Pin.OUT)
IN2 = Pin(9, Pin.OUT)
IN3 = Pin(4, Pin.OUT)
IN4 = Pin(5, Pin.OUT)

ENA = PWM(Pin(6), freq=1000)
ENB = PWM(Pin(7), freq=1000)

# Velocidades (0-1023)
vel_baja = 300
vel_media = 600
vel_alta = 900
vel_actual = vel_media

ENA.duty(vel_actual)
ENB.duty(vel_actual)

# Funciones
def stop():
    IN1.off(); IN2.off()
    IN3.off(); IN4.off()
    ENA.duty(0); ENB.duty(0)

def forward():
    IN1.on(); IN2.off()
    IN3.on(); IN4.off()
    ENA.duty(vel_actual)
    ENB.duty(vel_actual)

def backward():
    IN1.off(); IN2.on()
    IN3.off(); IN4.on()
    ENA.duty(vel_actual)
    ENB.duty(vel_actual)

def left():
    IN1.off(); IN2.on()
    IN3.on(); IN4.off()
    ENA.duty(vel_actual)
    ENB.duty(vel_actual)

def right():
    IN1.on(); IN2.off()
    IN3.off(); IN4.on()
    ENA.duty(vel_actual)
    ENB.duty(vel_actual)

def set_speed(v):
    global vel_actual
    vel_actual = int(v)
    ENA.duty(vel_actual)
    ENB.duty(vel_actual)

# Conexión WiFi
ssid = "Yatagarasu"
password = "MarioKart8Deluxe"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)
print("Conectando a WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("Conectado! IP:", wifi.ifconfig()[0])

# HTML
html = """<!DOCTYPE html>
<html>
<head>
<title>Control Carrito</title>
<style>
body {background:#222;color:white;font-family:Arial;text-align:center;}
button {width:140px;height:50px;margin:5px;font-size:18px;}
</style>
</head>
<body>
<h2>Control Carrito ESP32</h2>
<a href="/forward"><button>Adelante</button></a><br>
<a href="/left"><button>Izquierda</button></a>
<a href="/right"><button>Derecha</button></a><br>
<a href="/backward"><button>Atrás</button></a><br>
<a href="/stop"><button>Detener</button></a><br><br>
<a href="/speed300"><button>Velocidad Baja</button></a>
<a href="/speed600"><button>Velocidad Media</button></a>
<a href="/speed900"><button>Velocidad Alta</button></a>
</body>
</html>
"""

# Servidor
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("Servidor listo en http://{}".format(wifi.ifconfig()[0]))

# Loop principal
while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()
    print("Request:", request)

    if "/forward" in request: forward()
    elif "/backward" in request: backward()
    elif "/left" in request: left()
    elif "/right" in request: right()
    elif "/stop" in request: stop()
    elif "/speed" in request:
        try:
            v = int(request.split("/speed")[1].split()[0].replace("/", ""))
            set_speed(v)
        except: pass

    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()

