import fakeDelay from 'src/utils/FakeDelay';

const create = async (data) => {
  // const response = await fetch('/api/search');
  // const data = await response.json();
  // console.log(data);
  // return data;
  await fakeDelay(1000);
  return data;
};

const getById = async (id) => {
  await fakeDelay(1000);
  return id;
};

const delById = async (id) => {
  await fakeDelay(1000);
  return id;
};

const session = { create, getById, delById };

export default session;
