import { Fragment } from 'react';

// next
import dynamic from 'next/dynamic';

// project-imports
import DataCard from './DataCard';

// types
import { CardMiddleware } from 'types/org-chart';

// third-party
import { TreeNodeProps } from 'react-organizational-chart';

const TreeNode = dynamic<TreeNodeProps>(() => import('react-organizational-chart').then((mod) => mod.TreeNode), {
  ssr: false
});

// ==============================|| ORGANIZATION CHART - CARD ||============================== //

export default function Card({ items }: CardMiddleware) {
  return (
    <>
      {items.map((item: any, id: any) => (
        <Fragment key={id}>
          {item.children ? (
            <TreeNode
              label={
                <DataCard
                  name={item.name}
                  role={item.role}
                  avatar={item.avatar}
                  linkedin={item.linkedin}
                  facebook={item.facebook}
                  twitter={item.twitter}
                  root={false}
                />
              }
            >
              <Card items={item.children} />
            </TreeNode>
          ) : (
            <TreeNode
              label={
                <DataCard
                  name={item.name}
                  role={item.role}
                  avatar={item.avatar}
                  linkedin={item.linkedin}
                  facebook={item.facebook}
                  twitter={item.twitter}
                  root={false}
                />
              }
            />
          )}
        </Fragment>
      ))}
    </>
  );
}
