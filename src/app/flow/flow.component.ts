import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-flow',
  standalone: true,
  imports: [FormsModule, CommonModule, HttpClientModule],
  templateUrl: './flow.component.html',
  styleUrl: './flow.component.css'
})
export class FlowComponent {

  physicalWidth = 0.6;  // meters
  physicalHeight = 0.1; // meters
  widthNumber = 600;  // grid points along width
  heightNumber = 100; // grid points along height

  boundaryPressure = {
    inlet: 500,
    outlet: 0,
  };
  
  heatGrid: number[][] | null = null;
  initialImageFlow: string | null = null;
  evolvedImageFlow: string | null = null;
  showGrid = false;

  // parameters for temperature evolution calculation
  viscosity = 1e-3;
  dt = 1e-4;
  steps = 1000;

  constructor(private http: HttpClient) {}

  submitFlow() {
    const body = {
    widthNumber: this.widthNumber,
    heightNumber: this.heightNumber,
    physicalWidth: this.physicalWidth,
    physicalHeight: this.physicalHeight,
    boundaryPressure: {
      inlet: this.boundaryPressure.inlet,
      outlet: this.boundaryPressure.outlet,
    }
  };


    this.http.post<any>('http://localhost:8000/simulate_flow', body).subscribe({
      next: (res) => {
        this.heatGrid = res.grid;
        this.initialImageFlow = 'data:image/png;base64,' + res.image;
        this.showGrid = true;
      },
      error: (err) => console.error('API error:', err)
    });
  }

  submitFinalFlow() {
  const body = {
  widthNumber: this.widthNumber,
  heightNumber: this.heightNumber,
  physicalWidth: this.physicalWidth,
  physicalHeight: this.physicalHeight,
  viscosity: this.viscosity,
  dt: this.dt,
  steps: this.steps,
  boundaryPressure: {
    inlet: this.boundaryPressure.inlet,
    outlet: this.boundaryPressure.outlet,
  }
};

  this.http.post<any>('http://localhost:8000/simulate_evolution_flow', body).subscribe({
    next: (res) => {
      if (res.image) {
        this.evolvedImageFlow = 'data:image/png;base64,' + res.image;
        this.showGrid = true;
      } else {
        console.error('No image returned from backend');
        this.evolvedImageFlow = null;
      }
    },
    error: (err) => console.error('API error (evolution):', err)
  });
}

}
