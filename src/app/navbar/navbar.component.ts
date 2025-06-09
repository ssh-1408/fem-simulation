import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

declare var bootstrap: any;

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})

export class NavbarComponent {
  isNavbarOpen = false;

  toggleNavbar() {
    this.isNavbarOpen = !this.isNavbarOpen;
  }

  collapseNavbar() {
    const nav = document.getElementById('navbarNav');
    if (nav && nav.classList.contains('show')) {
      const bsCollapse = new bootstrap.Collapse(nav, { toggle: false });
      bsCollapse.hide();
      this.isNavbarOpen = false;
    }
  }
}
