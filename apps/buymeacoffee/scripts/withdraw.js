const hre = require("hardhat");
const abi = require("../artifacts/contracts/BuyMeACoffee.sol/BuyMeACoffee.json");

async function getBalance(provider, address) {
  const balance = await provider.getBalance(address);
  return hre.ethers.utils.formatEther(balance);
}

async function main() {
  const contractAddress = "0x9870059B51CD2532d0D7c8be465783873EbB9f22";
  const contractABI = abi.abi;

  const provider = new hre.ethers.providers.AlchemyProvider("goerli", process.env.GOERLI_API_KEY);

  const signer = new hre.ethers.Wallet(process.env.PRIVATE_KEY, provider);
  console.log("current balance of owner: ", await getBalance(provider, signer.address), "ETH");

  const contract = new hre.ethers.Contract(contractAddress, contractABI, signer);
  
  const contractBalance = await getBalance(provider, contract.address);
  console.log("current balance of contract: ", await getBalance(provider, contract.address), "ETH");

  if (contractBalance !== "0.0") {
    console.log("withdrawing funds..")
    const withdrawTxn = await contract.withdrawTips();
    await withdrawTxn.wait();
  } else {
    console.log("no funds to withdraw!");
  }
  console.log("current balance of owner: ", await getBalance(provider, signer.address), "ETH");
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });