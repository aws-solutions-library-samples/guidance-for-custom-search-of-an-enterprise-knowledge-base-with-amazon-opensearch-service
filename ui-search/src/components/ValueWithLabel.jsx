import { Box } from '@cloudscape-design/components';

const ValueWithLabel = ({ label, children }) => {
  // console.log({ children });
  return (
    <div>
      <Box variant="awsui-key-label">{label}</Box>
      <div>{children}</div>
    </div>
  );
};

export default ValueWithLabel;
