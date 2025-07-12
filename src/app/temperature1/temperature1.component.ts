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

  private readonly API_BASE_URL = 'http://localhost:8000/api';

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

    this.http.post<any>(`${this.API_BASE_URL}/simulate/`, body).subscribe({
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

  this.http.post<any>(`${this.API_BASE_URL}/simulate/evolution/`, body).subscribe({
    next: (res) => {
      if (res.task_id) {
        console.log(`Task submitted: ${res.task_id}`);
        this.pollTask(res.task_id);
      } else {
        console.error('No task_id returned');
      }
    },
    error: (err) => console.error('API error (evolution submit):', err)
  });
}

pollTask(taskId: string) {
  const interval = setInterval(() => {
    this.http.get<any>(`${this.API_BASE_URL}/simulate/task-status/${taskId}/`).subscribe({
      next: (res) => {
        if (res.status === 'SUCCESS' && res.result?.image) {
          this.evolvedImage = 'data:image/png;base64,' + res.result.image;
          this.showGrid = true;
          clearInterval(interval);
        } else if (res.status === 'FAILURE') {
          console.error('Task failed:', res.result?.error || 'Unknown error');
          clearInterval(interval);
        } else {
          console.log(`Task ${taskId} still running…`);
        }
      },
      error: (err) => {
        console.error('Error polling task:', err);
        clearInterval(interval);
      }
    });
  }, 2000); // poll every 2 seconds
}

}
