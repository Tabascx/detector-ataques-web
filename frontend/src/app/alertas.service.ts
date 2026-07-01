import { Injectable, signal } from '@angular/core';

export interface Alerta {
  ip: string;
  pais: string;
  tipo: string;
  intentos?: number;
  hora: string;
  severidad: 'alta' | 'media';
}

const SEVERIDAD_ALTA = ['SQL Injection', 'Command Injection', 'Fuerza Bruta'];

@Injectable({ providedIn: 'root' })
export class AlertasService {
  alertas = signal<Alerta[]>([]);
  conectado = signal<boolean>(false);

  private socket!: WebSocket;

  constructor() {
    this.conectar();
  }

  private conectar(): void {
    this.socket = new WebSocket('ws://localhost:8000/ws');

    this.socket.onopen = () => {
      this.conectado.set(true);
    };

    this.socket.onclose = () => {
      this.conectado.set(false);
      setTimeout(() => this.conectar(), 3000);
    };

    this.socket.onerror = () => {
      this.conectado.set(false);
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const nuevaAlerta: Alerta = {
        ip: data.ip,
        pais: data.pais,
        tipo: data.tipo,
        intentos: data.intentos,
        hora: new Date().toLocaleTimeString('es-ES'),
        severidad: SEVERIDAD_ALTA.includes(data.tipo) ? 'alta' : 'media',
      };
      this.alertas.update((lista) => [nuevaAlerta, ...lista]);
    };
  }
}
