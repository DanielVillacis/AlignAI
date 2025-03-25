import { Component, OnInit } from '@angular/core';
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
  selector: 'app-overview-chart',
  standalone: true,
  imports: [
    NgApexchartsModule
  ],
  templateUrl: './overview-chart.component.html',
  styleUrls: ['./overview-chart.component.scss']
})

export class OverviewChartComponent implements OnInit {
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

  tooltip: ApexTooltip = {
    enabled: true,
    shared: true,
    x: {
      format: 'MMM'
    },
    y: {
      formatter: function (value) {
        return value + ' patients'
      }
    }
  };


  constructor() {}

  ngOnInit(): void {
    this.generateChartData();
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
