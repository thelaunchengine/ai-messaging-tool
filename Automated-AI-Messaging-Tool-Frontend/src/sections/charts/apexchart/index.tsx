import React from 'react';
import { Grid } from '@mui/material';
import ApexAreaChart from './ApexAreaChart';
import ApexBarChart from './ApexBarChart';
import ApexColumnChart from './ApexColumnChart';
import ApexLineChart from './ApexLineChart';
import ApexMixedChart from './ApexMixedChart';
import ApexPieChart from './ApexPieChart';
import ApexPolarChart from './ApexPolarChart';
import ApexRadialChart from './ApexRadialChart';

const Apexcharts = () => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} lg={6}>
        <ApexAreaChart />
      </Grid>
      <Grid item xs={12} lg={6}>
        <ApexBarChart />
      </Grid>
      <Grid item xs={12} lg={6}>
        <ApexColumnChart />
      </Grid>
      <Grid item xs={12} lg={6}>
        <ApexLineChart />
      </Grid>
      <Grid item xs={12} lg={6}>
        <ApexMixedChart />
      </Grid>
      <Grid item xs={12} lg={6}>
        <ApexPieChart />
      </Grid>
      <Grid item xs={12} lg={6}>
        <ApexPolarChart />
      </Grid>
      <Grid item xs={12} lg={6}>
        <ApexRadialChart />
      </Grid>
    </Grid>
  );
};

export default Apexcharts;
