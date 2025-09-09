import React from 'react';
import { TreeView } from '@mui/x-tree-view/TreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';

const SimpleTreeView: React.FC = () => {
  return (
    <TreeView>
      <TreeItem nodeId='1' label='Item 1'>
        <TreeItem nodeId='2' label='Item 1.1' />
        <TreeItem nodeId='3' label='Item 1.2' />
      </TreeItem>
      <TreeItem nodeId='4' label='Item 2' />
    </TreeView>
  );
};

export default SimpleTreeView;
