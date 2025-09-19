import React from 'react';
import { Grid } from '@mui/material';
import Card from './Card';
import DataCard from './DataCard';

const OrgChart = () => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card />
      </Grid>
      <Grid item xs={12}>
        <DataCard />
      </Grid>
    </Grid>
  );
};

export default OrgChart;
