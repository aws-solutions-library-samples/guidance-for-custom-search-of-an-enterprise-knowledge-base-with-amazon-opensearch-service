import useLsApiGatewayUrls from 'src/hooks/useLsAppConfigs';
import fakeDelay from 'src/utils/FakeDelay';

export default async function search(query) {
  // const response = await fetch('/api/search');
  // const data = await response.json();
  // console.log(data);
  // return data;
  await fakeDelay(10 * 1000);
  return query;
}
