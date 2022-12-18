const hre = require("hardhat");

async function getBalance(address) {
    const balance = await hre.ethers.provider.getBalance(address);
    return hre.ethers.utils.formatEther(balance);
}
  
async function printBalances(addresses) {
    let idx = 0;
    for (const address of addresses) {
        console.log(`Address ${idx} balance: `, await getBalance(address));
        idx ++;
    }
}
  
async function printMemos(memos) {
    for (const memo of memos) {
        const timestamp = memo.timestamp;
        const tipper = memo.name;
        const tipperAddress = memo.from;
        const message = memo.message;
        console.log(`At ${timestamp}, ${tipper} (${tipperAddress}) said: "${message}"`);
    }
}

async function main() {
    const [owner, tipper, tipper2, tipper3] = await hre.ethers.getSigners();
    const ContractFactory = await hre.ethers.getContractFactory("BuyMeACoffee");
    const contract = await ContractFactory.deploy();
    await contract.deployed();
    console.log("BuyMeACoffee deployed at", contract.address);
    const addresses = [owner.address, tipper.address, contract.address];

    console.log("== start ==");
    await printBalances(addresses);

    const tip = {value: hre.ethers.utils.parseEther("0.01")};
    await contract.connect(tipper).buyCoffee("RedPanda", "Grrr...", tip);
    await contract.connect(tipper2).buyCoffee("Koala", "Mrrr...", tip);
    await contract.connect(tipper3).buyCoffee("PolarBear", "Brrr...", tip);

    console.log("== bought coffee ==");
    await printBalances(addresses);

    await contract.connect(owner).withdrawTips();

    console.log("== withdrewTips ==");
    await printBalances(addresses);
  
    console.log("== memos ==");
    const memos = await contract.getMemos();
    printMemos(memos);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
