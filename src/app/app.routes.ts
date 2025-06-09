import { Routes } from '@angular/router';
import { Temperature1Component } from './temperature1/temperature1.component';
import { HomeComponent } from './home/home.component';
import { FlowComponent } from './flow/flow.component';

export const routes: Routes = [
  { path: 'home', component: HomeComponent },
  { path: 'temperature1', component: Temperature1Component },
  { path: 'flow', component: FlowComponent },
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: '**', redirectTo: 'home' }
];
