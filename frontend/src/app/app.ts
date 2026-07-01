import { Component, computed, inject, signal } from '@angular/core';
import { AlertasService } from './alertas.service';

type Idioma = 'es' | 'en';

const TEXTOS = {
  es: {
    titulo: 'Detector de Ataques Web',
    subtitulo: 'Monitorizacion OWASP Top 10 en tiempo real',
    conectado: 'Conectado',
    desconectado: 'Desconectado',
    totalAlertas: 'Total Alertas',
    severidadAlta: 'Severidad Alta',
    paisesDetectados: 'Paises Detectados',
    alertasEnVivo: 'Alertas en Vivo',
    esperando: 'Esperando actividad sospechosa...',
    hora: 'Hora',
    ip: 'IP',
    pais: 'Pais',
    tipoAtaque: 'Tipo de Ataque',
    severidad: 'Severidad',
    alta: 'Alta',
    media: 'Media',
    simular: 'Simular Ataque',
    simulando: 'Simulando...',
    fuerzaBruta: 'Fuerza Bruta',
    intentos: 'int.',
  },
  en: {
    titulo: 'Web Attack Detector',
    subtitulo: 'Real-time OWASP Top 10 monitoring',
    conectado: 'Connected',
    desconectado: 'Disconnected',
    totalAlertas: 'Total Alerts',
    severidadAlta: 'High Severity',
    paisesDetectados: 'Countries Detected',
    alertasEnVivo: 'Live Alerts',
    esperando: 'Waiting for suspicious activity...',
    hora: 'Time',
    ip: 'IP',
    pais: 'Country',
    tipoAtaque: 'Attack Type',
    severidad: 'Severity',
    alta: 'High',
    media: 'Medium',
    simular: 'Simulate Attack',
    simulando: 'Simulating...',
    fuerzaBruta: 'Brute Force',
    intentos: 'att.',
  },
};

const TRADUCCION_TIPOS: Record<string, keyof typeof TEXTOS.es> = {
  'Fuerza Bruta': 'fuerzaBruta',
};

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private alertasService = inject(AlertasService);

  alertas = this.alertasService.alertas;
  conectado = this.alertasService.conectado;

  idioma = signal<Idioma>('es');
  t = computed(() => TEXTOS[this.idioma()]);
  simulando = signal(false);

  totalAlertas = computed(() => this.alertas().length);
  alertasAltas = computed(() => this.alertas().filter((a) => a.severidad === 'alta').length);
  paisesUnicos = computed(() => new Set(this.alertas().map((a) => a.pais)).size);

  cambiarIdioma(): void {
    this.idioma.update((actual) => (actual === 'es' ? 'en' : 'es'));
  }

  traducirTipo(tipo: string): string {
    const clave = TRADUCCION_TIPOS[tipo];
    return clave ? this.t()[clave] : tipo;
  }

  async simularRafaga(): Promise<void> {
    this.simulando.set(true);
    try {
      await fetch('http://localhost:8000/simular-rafaga', { method: 'POST' });
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setTimeout(() => this.simulando.set(false), 800);
    }
  }

  async simularAtaque(): Promise<void> {
    this.simulando.set(true);
    try {
      await fetch('http://localhost:8000/simular', { method: 'POST' });
    } catch (error) {
      console.error('Error al simular ataque:', error);
    } finally {
      setTimeout(() => this.simulando.set(false), 800);
    }
  }
}
