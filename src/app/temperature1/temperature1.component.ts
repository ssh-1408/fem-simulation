import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-temperature1',
  standalone: true,
  imports: [FormsModule, CommonModule, HttpClientModule],
  templateUrl: './temperature1.component.html',
  styleUrl: './temperature1.component.css'
})
export class Temperature1Component {

  private readonly API_BASE_URL = 'https://dg06jtexwx6ry.cloudfront.net';

  physicalWidth = 0.04;  // meters
  physicalHeight = 0.02; // meters
  widthNumber = 200;  // grid points along width
  heightNumber = 100; // grid points along height

  boundaryTemps = {
    top: 20,
    bottom: 0,
    left: 0,
    right: 20
  };
  
  heatGrid: number[][] | null = null;
  initialImage: string | null = null;
  evolvedImage: string | null = null;
  showGrid = false;

  // parameters for temperature evolution calculation
  alpha = 1e-4;
  dt = 0.0001;
  steps = 10000;

  constructor(private http: HttpClient) {}

  submit() {
    const body = {
      widthNumber: this.widthNumber,
      heightNumber: this.heightNumber,
      physicalWidth: this.physicalWidth,
      physicalHeight: this.physicalHeight,
      boundaryTemps: this.boundaryTemps
    };

    this.http.post<any>(`${this.API_BASE_URL}/simulate`, body).subscribe({
      next: (res) => {
        this.heatGrid = res.grid;
        this.initialImage = 'data:image/png;base64,' + res.image;
        this.showGrid = true;
      },
      error: (err) => console.error('API error:', err)
    });
  }

  submitFinal() {
  const body = {
    widthNumber: this.widthNumber,
    heightNumber: this.heightNumber,
    physicalWidth: this.physicalWidth,
    physicalHeight: this.physicalHeight,
    alpha: this.alpha,
    dt: this.dt,
    steps: this.steps,
    boundaryTemps: this.boundaryTemps
  };

  this.http.post<any>(`${this.API_BASE_URL}/simulate_evolution`, body).subscribe({
    next: (res) => {
      if (res.image) {
        this.evolvedImage = 'data:image/png;base64,' + res.image;
        this.showGrid = true;
      } else {
        console.error('No image returned from backend');
        this.evolvedImage = null;
      }
    },
    error: (err) => console.error('API error (evolution):', err)
  });
}

}
