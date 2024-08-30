#!/bin/bash

# Puertos a liberar
PORTS=(5000 80)

# Función para terminar procesos en un puerto dado
terminate_process_on_port() {
    PORT=$1
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo "Terminando proceso en el puerto $PORT con PID $PID..."
        sudo kill -9 $PID
        echo "Proceso terminado."
    else
        echo "No hay procesos ejecutándose en el puerto $PORT."
    fi
}

# Liberar los puertos
for PORT in "${PORTS[@]}"; do
    terminate_process_on_port $PORT
done

# Iniciar la aplicación Angular en el puerto 80
echo "Iniciando admin en el puerto 80..."
cd /home/ubuntu/frescapp/admin/app-admin/dist/app-admin
nohup sudo http-server --proxy http://localhost:80 -p 81 &

# Iniciar la aplicación Python en el puerto 5000
echo "Iniciando el backend en el puerto 5000..."
cd /home/ubuntu/frescapp/admin/backend
nohup sudo python3 app.py &

echo "Todas las aplicaciones han sido iniciadas."
