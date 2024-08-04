<script lang="ts">
  import { onMount } from "svelte";
  import { derived } from "svelte/store";
  import { page } from "$app/stores";
  import { toggleMode } from "mode-watcher";

  import {
    Plus,
    File,
    Home,
    LineChart,
    Ellipsis,
    PanelLeft,
    Settings,
    DollarSign,
    Package2,
    Search,
    UsersRound,
    UserRound,
  } from "lucide-svelte";

  /* import * as Accordion from "$lib/components/ui/accordion/index.js";
  import * as Avatar from "$lib/components/ui/avatar";
  import * as Pagination from "$lib/components/ui/pagination/index.js";
  import { Progress } from "$lib/components/ui/progress/index.js";
  import { Separator } from "$lib/components/ui/separator/index.js"; */

  import { Badge } from "$lib/components/ui/badge/index.js";
  import * as Breadcrumb from "$lib/components/ui/breadcrumb/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import * as Card from "$lib/components/ui/card/index.js";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import * as Sheet from "$lib/components/ui/sheet/index.js";
  import * as Table from "$lib/components/ui/table/index.js";
  import * as Tabs from "$lib/components/ui/tabs/index.js";
  import * as Tooltip from "$lib/components/ui/tooltip/index.js";
  import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";
  import * as Carousel from "$lib/components/ui/carousel/index.js";
  import * as Select from "$lib/components/ui/select";

  import Child from "$lib/components/ui/child/Child.svelte";
  import Chart from "$lib/components/ui/chart/Chart.svelte";
  import Map from "$lib/components/ui/map/Map.svelte";
  import AddPage from "$lib/components/ui/add/AddPage.svelte";
  import { List, Item } from "$lib/components/ui/list/index.js";
  import {
    userAuth,
    stores,
    selected,
    mode,
    notify,
    userMode,
    docTree,
  } from "$lib/store/store";

  import {
    doc,
    setDoc,
    getDocs,
    collection,
    deleteDoc,
  } from "firebase/firestore";
  import { db } from "$lib/firebase/firebase";
  let deviceList = [];

  let deviceChartData = [];
  let deviceChartExtra = [];

  let homeChartData = [];
  let combinedHomeChartData = [];
  
  let selectedHome = 0;
  let homeCardData = [];

  let totalEnergyStorage = 0;
  let totalEnergyProduction = 0;
  
  let totalPrevEnergyProduction = 0;
  let storageGain = 0;
  let productionGain = 0;
  let globalPeak = 0;

  let sumber = ["panel", "battery"];
  let totalDailyPowerBuffer = [[], []];
  let totalPrevDailyPowerBuffer = [[], []];

  let thisMonthPowerBuffer = [];
  let lastMonthPowerBuffer = [];
  
  let viewW = window.innerWidth;
  let viewH = window.innerHeight;
  let deviceScroll;

  function screenResize() {
    viewW = window.innerWidth;
    if (viewW < 640) deviceScroll = 40;
    else deviceScroll = 74;
  }
  screenResize();
  window.onresize = screenResize;

  function addDevice(event) {
    const { updatedObj } = event.detail;
    updatedObj.id = generateFirestoreDocumentId();
    deviceList.push(updatedObj);
    $stores.data.nodes = deviceList;
    // console.log($stores.data.nodes);
  }

  function removeDevice() {
    let index = $selected - 1;
    let newList = [...$stores.data.nodes].filter((val, i) => {
      return i != index;
    });
    $stores.data.nodes = newList;
    $selected = 0;
  }

  onMount(() => {
    setTimeout(() => {
      $notify = true;
    }, 3000);
  });

  function refresh() {
    let index = $selected - 1;
    $stores.data.nodes[index].settings.toggleUpdate = true;
    firebaseSync();
  }

  async function firebaseSync() {
    $notify = false;
    // console.log("Syncing");
    const existingNodes = new Set(); // Set to store existing node IDs

    try {
      // Get the current list of nodes from Firestore
      const querySnapshot = await getDocs(
        collection(db, "user", $stores.user.uid, "nodes")
      );
      querySnapshot.forEach((doc) => {
        existingNodes.add(doc.id); // Add each node ID to the set
      });

      // Loop through the array of node data
      for (const node of deviceList) {
        // Reference to the specific document in the subcollection
        const nodeDocRef = doc(db, "user", $stores.user.uid, "nodes", node.id);
        // Update the document with the content, excluding the id
        await setDoc(nodeDocRef, node, { merge: true });
        existingNodes.delete(node.id); // Remove the node ID from the set after updating
      }

      // Any remaining node IDs in the set are no longer in the deviceList and should be deleted
      for (const nodeId of existingNodes) {
        const nodeDocRef = doc(db, "user", $stores.user.uid, "nodes", nodeId);
        await deleteDoc(nodeDocRef); // Delete the document from Firestore
      }

      $notify = true;
    } catch (err) {
      console.error("There was an error syncing your information", err);
      $notify = true;
    }
  }

  $: {
    $mode = $page.url.searchParams.get("mode");
    // console.log($mode);
  }
  /* --=============== HELPER ===============-- */

  function generateFirestoreDocumentId() {
    const chars =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let autoId = "";
    for (let i = 0; i < 20; i++) {
      autoId += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return autoId;
  }

  function calculateBatteryPercentage(voltage) {
    const fullChargeVoltage = 12.73; // Voltage of a fully charged battery
    const dischargeVoltage = 11.36; // Voltage of a fully discharged battery

    if (voltage > fullChargeVoltage) {
      return 100; // Battery is fully charged or above
    } else if (voltage < dischargeVoltage) {
      return 0; // Battery is fully discharged or below
    } else {
      // Calculate the percentage of the battery's charge
      const percentage =
        ((voltage - dischargeVoltage) /
          (fullChargeVoltage - dischargeVoltage)) *
        100;
      return Math.round(percentage); // Round to the nearest whole number
    }
  }
  
  function addNestedArrays(arr1, arr2) {
	  // Check if both inputs are arrays
	  if (!Array.isArray(arr1) || !Array.isArray(arr2)) {
		throw new Error('Both inputs must be arrays.');
	  }

	  // Determine the longer array
	  const maxLength = Math.max(arr1.length, arr2.length);

	  // Create a new array to hold the results
	  const result = [];

	  for (let i = 0; i < maxLength; i++) {
		// Check if both elements are arrays
		if (Array.isArray(arr1[i]) && Array.isArray(arr2[i])) {
		  result.push(addNestedArrays(arr1[i], arr2[i]));
		} else if (Array.isArray(arr1[i])) {
		  result.push(arr1[i]);
		} else if (Array.isArray(arr2[i])) {
		  result.push(arr2[i]);
		} else {
		  // Add the elements if they exist in both arrays, otherwise take the existing element
		  result.push((arr1[i] || 0) + (arr2[i] || 0));
		}
	  }

	  return result;
	}

  function timeAgo(unixTimestamp) {
    const secondsAgo = Math.floor(Date.now() / 1000) - unixTimestamp;
    const minutesAgo = Math.floor(secondsAgo / 60);
    const hoursAgo = Math.floor(minutesAgo / 60);
    const daysAgo = Math.floor(hoursAgo / 24);
    const monthsAgo = Math.floor(daysAgo / 30);
    const yearsAgo = Math.floor(daysAgo / 365);

    if (yearsAgo > 0) return `${yearsAgo} year${yearsAgo > 1 ? "s" : ""}`;
    if (monthsAgo > 0) return `${monthsAgo} month${monthsAgo > 1 ? "s" : ""}`;
    if (daysAgo > 0) return `${daysAgo} day${daysAgo > 1 ? "s" : ""}`;
    if (hoursAgo > 0) return `${hoursAgo} hour${hoursAgo > 1 ? "s" : ""}`;
    if (minutesAgo > 0)
      return `${minutesAgo} minute${minutesAgo > 1 ? "s" : ""}`;
    return `${secondsAgo} second${secondsAgo > 1 ? "s" : ""}`;
  }

  /* --=============== STORES ===============-- */

  function fetchParams(chartDatas) {
    let now = new Date();
    let date = now.getDate();
    let current_time = now.toTimeString().split(" ")[0]; // "HH:MM:SS" format
    let start_time = new Date(now.setHours(6, 0, 0, 0))
      .toTimeString()
      .split(" ")[0];
    let end_time = new Date(now.setHours(18, 0, 0, 0))
      .toTimeString()
      .split(" ")[0];

    if (current_time >= start_time && current_time <= end_time) {
      let five_minutes = now.getHours() * 60 + now.getMinutes(); // 10;
      if (now.getDate() % 2) {
        five_minutes += 144;
      }
    }

    let evenDay = false;

    if (date % 2) {
      date += 31;
      evenDay = true;
    }

    let month = now.getMonth() + 1; // Get the current month (1-12)
    let isEvenMonth = month % 2 === 0;
    const tempDash = [];

    let dashChart = {
      "Battery": {
        labelss: [],
        values: [],
        title: [],
		yID: [],
		span:"daily"
      },
      "Solar Panel": {
        labelss: [],
        values: [],
		yID : [],
		span:"daily"
      },
	  "Power Points": {
        labelss: [],
        values: [],
		span:"scatter"
      },
    };
	
	let dashChartExtra = {
      "Battery": {
        labelss: [],
        values: [],
        title: [],
		filled: true,
		span:"daily",
		ylabel:"%",
      },
      "Solar Panel": {
        labelss: [],
        values: [],
		filled: false,
		span:"daily",
		ylabel:"°C",
      },
    };
	

	
	Object.assign(dashChart["Power Points"], chartDatas.curveIV);

    homeCardData = [];
    let currentDailyPowerBuffer = [[], []];
    let previousDailyPowerBuffer = [[], []];

    chartDatas.daily.labelss.forEach((units, index) => {
      sumber.forEach((sourced, urutan) => {
        let isSumber = units.indexOf(sourced);
        if (isSumber !== -1) {
          if (currentDailyPowerBuffer[urutan].length) {
            currentDailyPowerBuffer[urutan] = currentDailyPowerBuffer[urutan].map(
              function (num, idx) {
                return num * chartDatas.daily.values[index][idx];
              }
            );

            const middle = Math.ceil(currentDailyPowerBuffer[urutan].length / 2);
            if (evenDay) {
              previousDailyPowerBuffer[urutan] = currentDailyPowerBuffer[urutan].slice(
                0,
                middle
              );
              currentDailyPowerBuffer[urutan] =
                currentDailyPowerBuffer[urutan].slice(middle);
            } else {
              previousDailyPowerBuffer[urutan] =
                currentDailyPowerBuffer[urutan].slice(middle);
              currentDailyPowerBuffer[urutan] = currentDailyPowerBuffer[urutan].slice(
                0,
                middle
              );
            }
          } else currentDailyPowerBuffer[urutan] = chartDatas.daily.values[index];
        }
      });
    });

	// console.log("addarray",totalDailyPowerBuffer,currentDailyPowerBuffer)
	
	totalDailyPowerBuffer = addNestedArrays(totalDailyPowerBuffer,currentDailyPowerBuffer)
	totalPrevDailyPowerBuffer = addNestedArrays(totalPrevDailyPowerBuffer,previousDailyPowerBuffer)
	
	// console.log("powerbuf",currentDailyPowerBuffer)

    totalEnergyProduction +=
      currentDailyPowerBuffer[0].reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      ) / 12; // 12 jam, Wh

    totalEnergyStorage +=
      currentDailyPowerBuffer[1].reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      ) / 12;

    storageGain +=
      totalEnergyStorage -
      previousDailyPowerBuffer[1].reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      ) /
        12;

    productionGain +=
      totalEnergyProduction -
      previousDailyPowerBuffer[0].reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      ) /
        12;

    let currentPeak = currentDailyPowerBuffer[0].reduce(
      (a, b) => Math.max(a, b),
      -Infinity
    );
    let beforePeak = previousDailyPowerBuffer[0].reduce(
      (a, b) => Math.max(a, b),
      -Infinity
    );
	
	if (globalPeak > currentPeak) currentPeak = globalPeak;
	else globalPeak = currentPeak

    homeCardData.push({
      title: "Energy Production",
      values: totalEnergyProduction.toFixed(2) + " Wh",
      gain: productionGain.toFixed(2) + " Wh",
    });
    homeCardData.push({
      title: "Energy Storage",
      values: totalEnergyStorage.toFixed(2) + " Wh",
      gain: storageGain.toFixed(2) + " Wh",
    });
    homeCardData.push({
      title: "Peak Power",
      values: currentPeak.toFixed(2) + " W",
      gain: (currentPeak - beforePeak).toFixed(2) + " W",
    });
    homeCardData.push({
      title: "Device Count",
      values: deviceList.length,
      gain: 0,
    });
	
    

    chartDatas.daily.labelss.forEach((units, index) => {
      const middle = Math.ceil(chartDatas.daily.values[index].length / 2);
	  // console.log("middle",middle,chartDatas.daily.labelss[index])

      if (evenDay) {
        chartDatas.daily.values.push(
          chartDatas.daily.values[index].slice(0, middle)
        );
        chartDatas.daily.values[index] =
          chartDatas.daily.values[index].slice(middle);
      } else {
        chartDatas.daily.values.push(
          chartDatas.daily.values[index].slice(middle)
        );
        chartDatas.daily.values[index] = chartDatas.daily.values[index].slice(
          0,
          middle
        );
      }
      chartDatas.daily.labelss.push(`previous${units}`);
    });

    chartDatas.monthly.labelss.forEach((units, index) => {
      const middle = Math.ceil(chartDatas.monthly.values[index].length / 2);
      if (isEvenMonth) {
        chartDatas.monthly.values.push(
          chartDatas.monthly.values[index].slice(0, middle)
        );
        chartDatas.monthly.values[index] =
          chartDatas.monthly.values[index].slice(middle);
      } else {
        chartDatas.monthly.values.push(
          chartDatas.monthly.values[index].slice(middle)
        );

        chartDatas.monthly.values[index] = chartDatas.monthly.values[
          index
        ].slice(0, middle);
      }
      chartDatas.monthly.labelss.push(`previous${units}`);
    });
	
	chartDatas.monthly.labelss.forEach((units, index) => {
	// console.log("mons",chartDatas.monthly.values[index])
	if (units.indexOf("previous") !== -1) 
       thisMonthPowerBuffer = addNestedArrays(thisMonthPowerBuffer,chartDatas.monthly.values[index])
       else 
	   lastMonthPowerBuffer = addNestedArrays(lastMonthPowerBuffer,chartDatas.monthly.values[index])
	
	
	});
	// console.log("month", thisMonthPowerBuffer,lastMonthPowerBuffer);
	
	let capIndex = null;

    chartDatas.daily.labelss.forEach((units, index) => {
      let thing;
      let measure;
      let before;

      if (units.indexOf("oltage") !== -1) {
        measure = "Voltage";
      } else if (units.indexOf("urrent") !== -1) {
        measure = "Current";
      }
      if (units.indexOf("battery") !== -1) {
        thing = "Battery";
      } else if (units.indexOf("panel") !== -1) {
        thing = "Solar Panel";
      }
	  
	  
	  
      if (units.indexOf("prev") !== -1) {
        before = "Yesterday ";
		}
	  
	  if (units.indexOf("temp") !== -1) {
		capIndex = index
		dashChartExtra["Solar Panel"].labelss.push(
          (before ? before : "") + "Temperature"
        );
		dashChartExtra["Solar Panel"].values.push(chartDatas.daily.values[index])
      } else if (units.indexOf("soc") !== -1) {
		
		capIndex = index
		dashChartExtra["Battery"].labelss.push(
          (before ? before : "") + "State of Charge");
		
		dashChartExtra["Battery"].values.push(chartDatas.daily.values[index])
      } 
		

      if (thing != null) {
        
        //dashChart["daily"+before+thing+measure] = chartDatas.daily.values[index]
        dashChart[thing].labelss.push(
          (before ? before : "") + measure
        );
		
        dashChart[thing].values.push(chartDatas.daily.values[index]);
		dashChart[thing].yID.push(measure)
		
		//{ title: (before ? before : "") +thing+measure, type: "line", value:[chartDatas.daily.values[index]], timespan:"daily", labelss:before+thing+measure })
      }
	  
    });
	
	
	
	
    deviceChartData.push(dashChart);
deviceChartExtra.push(dashChartExtra);
    /* // console.log("compar", deviceChartData);
    // console.log("compar", deviceChartExtra);
   // console.log("compar", dashChart);
    // console.log("compar", chartDatas); 

    // console.log(
      "sumber",
      currentDailyPowerBuffer,
      previousDailyPowerBuffer,
      totalEnergyProduction,
      totalEnergyStorage,
      storageGain,
      productionGain,
      homeChartData
    ); */
  }

  stores.subscribe((curr) => {
    deviceList = curr.data.nodes;
    deviceChartData = [];
    homeChartData = [];
	thisMonthPowerBuffer = []
	lastMonthPowerBuffer = []
	
    deviceChartExtra = [];
    deviceList.forEach((device, nomorUrut) => {
      let chartsData = {};
      for (const [timespan, params] of Object.entries(device.stats)) {
        const labelss = [];
        const values = [];
        for (const [units, array] of Object.entries(params)) {
          labelss.push(units);
          values.push(array);
        }
        chartsData[timespan] = { labelss: labelss, values: values };
      }
      fetchParams(chartsData);

      // // console.log("deviceChartData", deviceChartData, nomorUrut, chartsData);
    });
	
	const tempChart = [];
		tempChart.push({
		  description:"Total Daily Power & Energy Production",
		  title: "Production",
		  type: "line",
		  width: "2",
		  value: [totalDailyPowerBuffer[0]],
		  timespan: "daily",
		  labelss: ["Power & Energy"],
		  filled: true
		});
		tempChart.push({
			
		  description:"Total Monthly Power Production",
		  title: "Production",
		  type: "bar",
		  width: "1",
		  value: [thisMonthPowerBuffer,lastMonthPowerBuffer],
		  timespan: "monthly",
		  labelss: ["This Month","Last Month"],
		  filled: false
		});

		homeChartData.push(tempChart);

    // combinedChartData = combineChartData(deviceChartData);

    // // console.log("combinedChartData",combinedChartData);
  });

  // // console.log("deviceList", deviceList);

  let deviceLocations = derived(stores, ($stores) => {
    if ($stores && $stores.data.nodes) {
      let modelsLocation = $stores.data.nodes.map((nodes) => nodes.details);
      return modelsLocation;
    }
    return [];
  });
</script>

{#if !$stores.loading}
  <div class="flex min-h-screen w-full flex-col bg-muted/40">
    <aside
      class="fixed inset-y-0 left-0 z-10 hidden w-14 flex-col border-r bg-background sm:flex nav-mobile"
    >
      <nav class="flex flex-col items-center gap-4 px-2 py-4">
        <a
          href="##"
          class="group flex h-9 w-9 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:h-8 md:w-8 md:text-base"
        >
          <Package2 class="h-4 w-4 transition-all group-hover:scale-110" />
          <span class="sr-only">Acme Inc</span>
        </a>

        {#if $userMode == "admin"}
          <Tooltip.Root>
            <Tooltip.Trigger asChild let:builder>
              <a
                href="?mode=Admin"
                class="flex h-9 w-9 items-center justify-center rounded-lg {$mode ==
                'Admin'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground'} transition-colors hover:text-foreground md:h-8 md:w-8"
                use:builder.action
                {...builder}
              >
                <UsersRound class="h-5 w-5" />
                <span class="sr-only">Admin</span>
              </a>
            </Tooltip.Trigger>
            <Tooltip.Content side="right">Admin</Tooltip.Content>
          </Tooltip.Root>
        {:else}
          <Tooltip.Root>
            <Tooltip.Trigger asChild let:builder>
              <a
                href="?mode=Home"
                class="flex h-9 w-9 z-30 items-center justify-center rounded-lg {$mode ==
                'Home'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground'} transition-colors hover:text-foreground md:h-8 md:w-8"
                use:builder.action
                {...builder}
              >
                <Home class="h-5 w-5" />
                <span class="sr-only">Dashboard</span>
              </a>
            </Tooltip.Trigger>
            <Tooltip.Content side="right">Dashboard</Tooltip.Content>
          </Tooltip.Root>
          <Tooltip.Root>
            <Tooltip.Trigger asChild let:builder>
              <a
                href="?mode=Monitor"
                class="flex h-9 w-9 z-30 items-center justify-center rounded-lg {$mode ==
                'Monitor'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground'} transition-colors hover:text-foreground md:h-8 md:w-8"
                use:builder.action
                {...builder}
              >
                <LineChart class="h-5 w-5" />
                <span class="sr-only">Analytics</span>
              </a>
            </Tooltip.Trigger>
            <Tooltip.Content side="right">Analytics</Tooltip.Content>
          </Tooltip.Root>
        {/if}
      </nav>
      <nav class="mt-auto flex flex-col items-center gap-4 px-2 py-4">
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild let:builder>
            <Button builders={[builder]} class="h-5 w-5" variant="outline">
              <Tooltip.Root>
                <Tooltip.Trigger asChild let:builder>
                  <div
                    class="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8"
                    use:builder.action
                    {...builder}
                  >
                    <Settings />
                    <span class="sr-only">Settings</span>
                  </div>
                </Tooltip.Trigger>
                <Tooltip.Content side="right">Settings</Tooltip.Content>
              </Tooltip.Root>
            </Button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Content align="end">
            <Button on:click={toggleMode} variant="outline" size="icon">
              <i class="fa-solid fa-moon"></i>
              <span class="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenu.Content>
        </DropdownMenu.Root>
      </nav>
    </aside>
    <div class="flex flex-col sm:py-4 sm:pl-14">
      <header
        class="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6"
      >
        <Sheet.Root>
          <Sheet.Trigger asChild let:builder>
            <Button
              builders={[builder]}
              size="icon"
              variant="outline"
              class="sm:hidden"
            >
              <PanelLeft class="h-5 w-5" />
              <span class="sr-only">Toggle Menu</span>
            </Button>
          </Sheet.Trigger>
          <Sheet.Content side="left" class="sm:max-w-xs">
            <nav class="grid gap-6 text-lg font-medium">
              <a
                href="##"
                class="group flex h-10 w-10 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:text-base"
              >
                <Package2
                  class="h-5 w-5 transition-all group-hover:scale-110"
                />
                <span class="sr-only">SCC PKTJ</span>
              </a>
              <Button on:click={toggleMode} variant="outline" size="icon">
                <i class="fa-solid fa-moon"></i>
                <span class="sr-only">Toggle theme</span>
              </Button>
              {#if ["Admin"].includes($mode)}
                <a
                  href="?mode=Admin"
                  class="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                >
                  <UsersRound class="h-5 w-5" />
                  Admin
                </a>
              {:else}
                <a
                  href="?mode=Home"
                  class="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                >
                  <Home class="h-5 w-5" />
                  Home
                </a>

                <a
                  href="?mode=Monitor"
                  class="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                >
                  <LineChart class="h-5 w-5" />
                  Monitor
                </a>
              {/if}
            </nav>
          </Sheet.Content>
        </Sheet.Root>
        <Breadcrumb.Root class="hidden md:flex">
          <Breadcrumb.List>
            <Breadcrumb.Item>
              <Breadcrumb.Link href="">Dashboard</Breadcrumb.Link>
            </Breadcrumb.Item>
            <Breadcrumb.Separator />
            <Breadcrumb.Item>
              <Breadcrumb.Link href="?mode={$mode}">{$mode}</Breadcrumb.Link>
            </Breadcrumb.Item>
          </Breadcrumb.List>
        </Breadcrumb.Root>
        <!-- {#if ["Home"].includes($mode) && deviceList}
          <div>
            <Select.Root
              selected={selectedHome}
              onSelectedChange={(v) => {
                // console.log("v", v.value);
                selectedHome = v.value;
              }}
            >
              <Select.Trigger id="category" aria-label="Select category">
                <Select.Value placeholder="Select device" />
              </Select.Trigger>
              <Select.Content>
                {#each deviceList as item, i}
                  <Select.Item value={i} label={item.name}
                    >{item.name}
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>
        {/if} -->
        <div class="relative gap-2 ml-auto flex-1 flex flex-row md:grow-0">
          <Search
            class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"
          />
          <Input
            type="search"
            placeholder="Search..."
            class="w-full rounded-lg bg-background pl-8 md:w-[200px] lg:w-[320px]"
          />

          {#if ["Admin", "Home"].includes($mode)}
            <Button
              variant="outline"
              class="h-10 gap-1 text-sm"
              onclick="window.print()"
            >
              <File class="h-3.5 w-3.5" />
              <span class="sr-only sm:not-sr-only">Export</span>
            </Button>
          {/if}
        </div>
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild let:builder>
            <Button
              variant="outline"
              size="icon"
              class="overflow-hidden rounded-full"
              builders={[builder]}
            >
              <UserRound class="overflow-hidden rounded-full h-5 w-5" />
            </Button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Content align="end">
            <DropdownMenu.Label>My Account</DropdownMenu.Label>
            <DropdownMenu.Separator />
            <DropdownMenu.Item>Settings</DropdownMenu.Item>
            <DropdownMenu.Item>Support</DropdownMenu.Item>
            <DropdownMenu.Separator />
            <DropdownMenu.Item on:click={userAuth.logout}
              >Logout</DropdownMenu.Item
            >
          </DropdownMenu.Content>
        </DropdownMenu.Root>
      </header>
      {#if ["Monitor", "Add"].includes($mode)}
        <main
          class="grid flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 sm:grid-rows-1 md:gap-8 lg:grid-cols-3 xl:grid-cols-3"
        >
          {#if viewW < 640}
            <div
              class="grid row-span-1 md:auto-rows-max items-start gap-2 md:gap-4 lg:col-span-2"
            >
              <Tabs.Root value="map">
                <div class="flex items-center">
                  <Tabs.List>
                    <Tabs.Trigger value="map">Map</Tabs.Trigger>
                    {#if $selected}
                      <Tabs.Trigger value="cam">Camera</Tabs.Trigger>

                      <Tabs.Trigger value="stats">Stats</Tabs.Trigger>
                    {/if}
                  </Tabs.List>
                  <div class="ml-auto flex items-center gap-2">
                    {#if viewW < 640}
                      <Button
                        size="sm"
                        href="?mode={$mode == 'Monitor' ? 'Add' : 'Monitor'}"
                        variant="outline"
                        class="h-7 gap-1 text-sm"
                        type="button"
                      >
                        <Plus class="h-3.5 w-3.5" />
                        <span class="sr-only sm:not-sr-only">Add</span>
                      </Button>
                    {/if}
                    <Button
                      variant="outline"
                      size="sm"
                      class="h-7 gap-1 text-sm"
                      on:click={firebaseSync}
                    >
                      <i class="bx bx-sync" />
                      <span class="sr-only sm:not-sr-only">Sync All</span>
                    </Button>
                  </div>
                </div>
                <Tabs.Content value="cam">
                  <Card.Root>
                    <Card.Header class="p-0 map-div">
                      {#if $selected}
                        <img
						alt="Please connect to Tailscale Network"
                          style="display: block;-webkit-user-select: none;margin: auto;background-color: hsl(0, 0%, 25%);"
                          src="http://{deviceList[$selected - 1].settings
                            .tailscaleIP}:8081/"
                          width="375"
						  height="281"
                        />
						<!-- width="375"
                          height="281" -->
                      {/if}
                    </Card.Header>
                  </Card.Root>
                </Tabs.Content>
                <Tabs.Content value="map">
                  <Card.Root>
                    <Card.Header class="p-0">
                      <div class=" map-full">
                        <Map pins={$deviceLocations} />
                      </div>
                    </Card.Header>
                  </Card.Root>
                </Tabs.Content>

                {#if $selected}
                  <div
                    class="grid gap-4 sm:grid-cols-2 pr-8 pl-8 md:grid-cols-2 md:max-w-4xl lg:grid-cols-2 xl:grid-cols-2"
                  >
                    <Tabs.Content
                      class=" h-full  sm:col-span-2"
                      style="max-width:75vw"
                      value="stats"
                    >
                      <Carousel.Root class="map-full">
                        <Carousel.Content>
                          {#each Object.entries(deviceChartData[$selected - 1]) as [timespan, dataset], i}
                            <Carousel.Item>
                              <div class="p-1">
                                <Card.Root>
                                  <Card.Content
                                    class="flex flex-col items-center justify-center p-6"
                                  >
                                    <p>{timespan}</p>
									<Chart
									  labelss={dataset.labelss}
									  values={dataset.values}
									  span={dataset.span}
									  type={dataset.span}
									  
									  title={timespan}
                                      width="100%"
                                      height="65vh"
									  yID={dataset.yID}
									  
									/>
                                    
                                  </Card.Content>
                                </Card.Root>
                              </div>
                            </Carousel.Item>
                          {/each}
                        </Carousel.Content>
                        <Carousel.Previous />
                        <Carousel.Next />
                      </Carousel.Root>
                    </Tabs.Content>
                  </div>
                {/if}
              </Tabs.Root>
            </div>
          {:else}
          <ScrollArea class="h-[86vh]  col-span-2 auto-rows-max">
            <div
              class="grid  grid grid-cols-3 grid-rows-4  items-start gap-2"
            >
			{#if $selected}
			<div class="grid w-full col-span-1 map-div">
				
                  <Card.Root>
                    <Card.Header class="flex pt-1 flex-col items-center justify-center p-0">
					<p>Power Points</p>
                      <Chart
						  labelss={deviceChartData[$selected - 1]["Power Points"].labelss}
						  values={deviceChartData[$selected - 1]["Power Points"].values}
						  title="Power Points"
						  type={deviceChartData[$selected - 1]["Power Points"].span}
						  span={deviceChartData[$selected - 1]["Power Points"].span}
						  axisYLabel="A"
						  axisXLabel="V"
						  width="90%"
						  height="100%"
						  displayLegend = {true}
						/>
						
                    </Card.Header>
                  </Card.Root>
				  
                </div>
				{/if}
              <div
                class="grid {$selected
                  ? 'map-div col-span-1'
                  : 'map-full col-span-3 row-span-4'}"
              >
                <Map pins={$deviceLocations} />
              </div>
              {#if $selected}
                <div class="grid col-span-1 map-div">
                  <Card.Root>
                    <Card.Header class="p-0 w-full h-full">
                      <img
					  alt="Please connect to Tailscale Network"
                        class="w-full h-full"
						style="display: block; width:100% height:100% -webkit-user-select: none;margin: auto;background-color: hsl(0, 0%, 25%);"
                        src="http://{deviceList[$selected - 1].settings
                          .tailscaleIP}:8081/"
						width="375"
						height="281"
                      />
                    </Card.Header>
                  </Card.Root>
                </div>
				
                <div class="grid col-span-3 h-full row-span-3" style="overflow:hidden">
                  <Carousel.Root
                    class="w-full sm:col-span-2"
                    style="max-width:60vw"
                  >
                    <Carousel.Content>
                      {#each Object.entries(deviceChartData[$selected - 1]) as [timespan, dataset], i}
                        <Carousel.Item>
                          <div class="p-1">
                            <Card.Root>
                              <Card.Content
                                class="flex pt-1 flex-col items-center justify-center"
                              >
                                <p>{timespan}</p>
								
                                <Chart
                                  labelss={dataset.labelss}
                                  values={dataset.values}
                                  span={dataset.span}
								  type={dataset.span}
								  
								  title={timespan}
                                  width="100%"
                                  height="46vh"
								  yID={dataset.yID}
								  
                                />
								{#if deviceChartExtra[$selected - 1][timespan]}
								<Chart
                                  values={deviceChartExtra[$selected - 1][timespan].values}
								  labelss={deviceChartExtra[$selected - 1][timespan].labelss}
								  title={timespan}
                                  type={deviceChartExtra[$selected - 1][timespan].span}
                                  span={deviceChartExtra[$selected - 1][timespan].span}
                                  axisYLabel = {deviceChartExtra[$selected - 1][timespan].ylabel}
								  width="100%"
                                  height="20vh"
								  filled={deviceChartExtra[$selected - 1][timespan].filled}
								  displayX = {false}
								  displayLegend = {false}								  
                                />
								{/if}
                              </Card.Content>
                            </Card.Root>
                          </div>
                        </Carousel.Item>
                      {/each}
                    </Carousel.Content>
                    <Carousel.Previous />
                    <Carousel.Next />
                  </Carousel.Root>
                </div>
              {/if}
            </div>
          </ScrollArea>
          {/if}

          <div>
            <div class="flex pt-2 pb-4 items-center justify-between mobile-hide">
              <h1 class="text-lg font-semibold md:text-2xl">Device {$mode}</h1>
              <div>
                <Button
                  variant="outline"
                  size="sm"
                  class="h-7 gap-1 text-sm"
                  on:click={firebaseSync}
                >
                  <i class="bx bx-sync" />
                  <span class="sr-only sm:not-sr-only">Sync All</span>
                </Button>

                <Button
                  size="sm"
                  href="?mode={$mode == 'Monitor' ? 'Add' : 'Monitor'}"
                  variant="outline"
                  class="h-7 gap-1 text-sm"
                  type="button"
                >
                  <Plus class="h-3.5 w-3.5" />
                  <span class="sr-only sm:not-sr-only">Add</span>
                </Button>
              </div>
            </div>
            <ScrollArea class="h-[45vh] sm:h-[78vh] rounded-md mobile-hide">
              {#if $mode == "Add"}
                <AddPage on:add={addDevice} />
              {:else}
                <List collapse --background="#ffffff" --color="#000000">
                  {#each deviceList as item, i}
                    <Item
                      order={i + 1}
                      --hover="#bbbbbb"
                      --content-padding="0px"
                    >
                      <svelte:fragment slot="title">
                        <div class="device-name">
                          <img
                            src="assets/items/{item.details.type}.png"
                            class="device-icon"
                          />
                          <div class="device-title">
                            <p style="font-size:1.2rem;">{item.name}</p>
                            <p style="font-size:10px;">
                              {item.id}
                            </p>
                            <p style="font-size:10px;">
                              {timeAgo(item.details.lastUpdate)} ago
                            </p>
                            {#if $selected}
                              <div class="device-btns">
                                <button on:click={removeDevice}
                                  ><i class="fa-solid fa-xmark"></i></button
                                >
                                <button on:click={refresh}>
                                  {#if !item.settings.toggleUpdate}
                                    <i class="bx bx-sync"></i>
                                  {:else}
                                    <i
                                      class="fa-solid fa-spinner loadingSpinner"
                                    />
                                  {/if}
                                </button>
                              </div>
                            {/if}
                          </div>
                        </div>
                        <div style="display:flex; flex-direction:column; align-items:right;">
                          <div
                            style="display:flex; flex-direction:row; align-items:center;"
                          >
                            <i class="fa-solid fa-solar-panel"></i>
                            <p>
                              &nbsp{(item.readings.panelVoltage *
                                item.readings.panelCurrent) |
                                0}W
                            </p>
                          </div>

                          <div
                            style="display:flex; flex-direction:row; align-items:center; color:{calculateBatteryPercentage(
                              item.readings.batteryVoltage
                            ) > 90
                              ? 'green'
                              : calculateBatteryPercentage(
                                    item.readings.batteryVoltage
                                  ) < 10
                                ? 'red'
                                : 'orange'}"
                          >
                            <i class="fa-solid fa-car-battery"></i>
                            <p>
                              &nbsp{calculateBatteryPercentage(
                                item.readings.batteryVoltage
                              )}%
                            </p>
                          </div>
						  <div
                            style="display:flex; flex-direction:row; align-items:center;"
                          >
                            <i class="fa-solid fa-temperature-half"></i>
                            <p>
                              &nbsp{(item.readings.temp) |
                                0}°C
                            </p>
                          </div>
						  
                        </div>
						&nbsp&nbsp
                      </svelte:fragment>
                      <svelte:fragment slot="content">
                        <div class="device-content">
                          <Child settings={item} />
                        </div></svelte:fragment
                      >
                    </Item>
                  {/each}
                </List>
              {/if}
            </ScrollArea>
          </div>
        </main>
      {:else if ["Admin"].includes($mode)}
        <main class="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
          <Card.Root>
            <Card.Header>
              <Card.Title>Database</Card.Title>
              <Card.Description>Users and devices connected.</Card.Description>
            </Card.Header>
            <Card.Content>
              <Table.Root>
                <Table.Header>
                  <Table.Row>
                    <Table.Head class="hidden w-[100px] sm:table-cell">
                      <span class="sr-only">Image</span>
                    </Table.Head>
                    <Table.Head>Name</Table.Head>
                    <Table.Head>ID</Table.Head>
                    <Table.Head class="hidden md:table-cell"
                      >Created at</Table.Head
                    >
                    <Table.Head>
                      <span class="sr-only">Actions</span>
                    </Table.Head>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {#each $docTree as user, indeks}
                    <Table.Row>
                      <Table.Cell class="hidden sm:table-cell">
                        <i class="fa-regular fa-user"></i>
                      </Table.Cell>
                      <Table.Cell class="font-medium"
                        >{user.details.profile.email}</Table.Cell
                      >
                      <Table.Cell>
                        <Badge variant="outline">{user.userId}</Badge>
                      </Table.Cell>
                      <Table.Cell class="hidden md:table-cell">
                        2023-07-12 10:42 AM
                      </Table.Cell>
                      <Table.Cell>
                        <DropdownMenu.Root>
                          <DropdownMenu.Trigger asChild let:builder>
                            <Button
                              aria-haspopup="true"
                              size="icon"
                              variant="ghost"
                              builders={[builder]}
                            >
                              <Ellipsis class="h-4 w-4" />
                              <span class="sr-only">Toggle menu</span>
                            </Button>
                          </DropdownMenu.Trigger>
                          <DropdownMenu.Content align="end">
                            <DropdownMenu.Label>Actions</DropdownMenu.Label>
                            <DropdownMenu.Item>Edit</DropdownMenu.Item>
                            <DropdownMenu.Item>Delete</DropdownMenu.Item>
                          </DropdownMenu.Content>
                        </DropdownMenu.Root>
                      </Table.Cell>
                    </Table.Row>
                    {#if $docTree[indeks].nodes.length}
                      {#each $docTree[indeks].nodes as device, index}
                        <Table.Row>
                          <Table.Cell class="hidden sm:table-cell">
                            &nbsp<i class="fa-solid fa-solar-panel"></i>
                          </Table.Cell>
                          <Table.Cell class="font-medium"
                            ><pre>    {device.name}</pre></Table.Cell
                          >
                          <Table.Cell>
                            <Badge variant="outline">{device.id}</Badge>
                          </Table.Cell>
                          <Table.Cell class="hidden md:table-cell">
                            2023-07-12 10:42 AM
                          </Table.Cell>
                          <Table.Cell>
                            <DropdownMenu.Root>
                              <DropdownMenu.Trigger asChild let:builder>
                                <Button
                                  aria-haspopup="true"
                                  size="icon"
                                  variant="ghost"
                                  builders={[builder]}
                                >
                                  <Ellipsis class="h-4 w-4" />
                                  <span class="sr-only">Toggle menu</span>
                                </Button>
                              </DropdownMenu.Trigger>
                              <DropdownMenu.Content align="end">
                                <DropdownMenu.Label>Actions</DropdownMenu.Label>
                                <DropdownMenu.Item>Edit</DropdownMenu.Item>
                                <DropdownMenu.Item>Delete</DropdownMenu.Item>
                              </DropdownMenu.Content>
                            </DropdownMenu.Root>
                          </Table.Cell>
                        </Table.Row>
                      {/each}
                    {/if}
                  {/each}
                </Table.Body>
              </Table.Root>
            </Card.Content>
            <Card.Footer>
              <div class="text-xs text-muted-foreground">
                Showing <strong>1-10</strong> of <strong>32</strong> products
              </div>
            </Card.Footer>
          </Card.Root>
        </main>
      {:else if ["Home"].includes($mode) && deviceList}
        <main
          class="flex flex-1 flex-col gap-2 p-4 md:gap-4 md:p-4 printableArea"
        >
          <div class="grid h-auto  gap-4 md:gap-8 lg:grid-cols-2 xl:grid-cols-4">
            {#each homeCardData as element, index}
              <Card.Root
                data-x-chunk-name="dashboard-01-chunk-0"
                data-x-chunk-description="A card showing the total revenue in USD and the percentage difference from last month."
              >
                <Card.Header
                  class="flex flex-row items-center justify-between space-y-0 pb-2"
                >
                  <Card.Title class="text-sm font-medium"
                    >{element.title}</Card.Title
                  >
                  <DollarSign class="h-4 w-4 text-muted-foreground" />
                </Card.Header>
                <Card.Content>
                  <div class="text-2xl font-bold">{element.values}</div>
                  {#if element.gain}
					
                    <p class="text-xs text-muted-foreground">
                      {element.gain} from yesterday
                    </p>
                  {/if}
                </Card.Content>
              </Card.Root>
            {/each}
          </div>

          <div class="grid h-[52vh] gap-4 md:gap-8 grid-cols-1 xl:grid-cols-3">
            {#each homeChartData[selectedHome] as element, index}
              <Card.Root
                class="h-full lg:col-span-{element.width}"
                data-x-chunk-name="dashboard-01-chunk-{index}"
                data-x-chunk-description="A card showing a table of recent transactions with a link to view all transactions."
              >
                <Card.Header class="flex flex-row items-center">
                  <div class="grid gap-2">
                    <Card.Title>{element.description}</Card.Title>
                  </div>
                </Card.Header>
                <Card.Content class="h-[50vh]">
                  <Chart
                    title={element.title}
                    span={element.timespan}
                    labelss={element.labelss}
                    values={element.value}
                    type={element.type}
					filled={element.filled}
                    width="100%"
                    height="100%"
                  />
                </Card.Content>
              </Card.Root>
            {/each}
          </div>
        </main>
      {/if}
    </div>
  </div>
{/if}

<style>
  .not-shown {
    position: fixed;
    width: 27vw;
  }

  .device-icon {
    padding-right: 10px;
    height: 3rem;
    width: auto;
  }

  .carousel-max-width {
    max-width: 75vw;
  }

  .device-name {
    display: flex;
    flex-direction: row;
    width: 100%;
    justify-content: left;
    align-items: center;
  }
  .device-content {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .map-full {
    border-radius: 12px;
    height: 85vh;
  }

  .map-div {
    border-radius: 12px;
    height: 30vh;
  }
  .max-height-set {
    height: 90vh;
  }

  @media print {
    aside {
      visibility: hidden;
    }
    header {
      visibility: hidden;
    }
    #printableArea,
    #printableArea * {
      visibility: visible;
    }
    #printableArea {
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: auto;
      z-index: 1000;
      background: white; /* Ensure background is white */
      padding: 20px; /* Add padding if needed */
    }
    /* Optional: Handle page breaks */
    .page-break {
      page-break-before: always;
    }
  }

  .loadingSpinner {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  @media (max-width: 640px) {
    .map-full {
      border-radius: 12px;
      height: 30vh;
    }

    .map-div {
      border-radius: 12px;
      height: 30vh;
    }
    .nav-mobile {
    }
    .mobile-hide {
      display: none;
    }
    .not-shown {
      width: 89%;
    }
  }
</style>
