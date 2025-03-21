import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatDatepickerModule} from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { provideNativeDateAdapter } from '@angular/material/core';
import { NgxChartsModule, LegendPosition } from '@swimlane/ngx-charts';
import * as shape from 'd3-shape';
import { group } from '@angular/animations';
import { NgApexchartsModule } from 'ng-apexcharts';

import {
  ApexChart,
  ApexAxisChartSeries,
  ApexStroke,
  ApexDataLabels,
  ApexXAxis,
  ApexYAxis,
  ApexLegend,
  ApexFill,
  ApexTooltip,
  ApexGrid
} from 'ng-apexcharts';

// Define chart options type
export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  stroke: ApexStroke;
  dataLabels: ApexDataLabels;
  yaxis: ApexYAxis;
  colors: string[];
  labels: string[];
  legend: ApexLegend;
  fill: ApexFill;
  tooltip: ApexTooltip;
  grid: ApexGrid;
};


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, 
    MatDatepickerModule, 
    MatNativeDateModule,
    NgApexchartsModule
  ],
  providers: [provideNativeDateAdapter()],
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss'],
})

export class HomePageComponent implements OnInit {
  selectedDate: Date | null = null;
  scheduledEvents: any[] = [];
  scans: any[] = [];

  // ------------- Apex Chart -------------
  // ApexCharts configuration
  series: ApexAxisChartSeries = [];
  chart: ApexChart = {
    height: 300,
    type: 'area',
    toolbar: {
      show: false
    },
    zoom: {
      enabled: false
    }
  };
  dataLabels: ApexDataLabels = {
    enabled: false
  };
  stroke: ApexStroke = {
    curve: 'smooth',
    width: 2
  };
  xaxis: ApexXAxis = {
    type: 'category',
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    tickPlacement: 'on'
  };
  yaxis: ApexYAxis = {
    title: {
      text: '',
    },
    labels: {
      show: false
    },
    axisTicks: {
      show: false
    },
    axisBorder: {
      show: false
    }
  };
  colors: string[] = ['#3EC9B9', '#303545'];
  legend: ApexLegend = {
    position: 'bottom'
  };
  fill: ApexFill = {
    type: 'gradient',
    gradient: {
      shadeIntensity: 0.5,
      opacityFrom: 0.6,
      opacityTo: 0.3,
      stops: [40, 90, 100]
    }
  };
  labels: string[] = [];

  grid: ApexGrid = {
    show: true,
    borderColor: 'transparent',
    xaxis: {
      lines: {
        show: false // Hide vertical grid lines
      }
    },
    yaxis: {
      lines: {
        show: false // Hide horizontal grid lines
      }
    },
    padding: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    }
  };



  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.getScans();
    this.generateChartData();
  }

  onDateSelected(date: Date) {
    this.selectedDate = date;
    // Here you would fetch events for the selected date
    // this.getEventsForDate(date);
  }

  getScans() {
    this.http.get<any[]>('http://127.0.0.1:5000/api/scans')
      .subscribe({
        next: (data) => {
          this.scans = data;
          this.generateChartData(); // for updating the chart when the data is fetched
        },
        error: (error) => {
          console.error('There was an error!', error);
        }
      }
      );
  }

  generateChartData() {
    // Sample data for the chart
    this.series = [
      {
        name: 'New Patients',
        data: [31, 40, 28, 51, 42, 109, 100, 50, 60, 70, 80, 90]
      },
      {
        name: 'Returning Patients',
        data: [11, 32, 45, 32, 34, 52, 41, 21, 31, 41, 51, 61]
      }
    ];
  }

}
