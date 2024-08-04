<!-- AddPage.svelte -->
<script>
  import { createEventDispatcher } from "svelte";
  import Child from "$lib/components/ui/child/Child.svelte";
  
  import { mapCenter, mode } from "$lib/store/store";

  let entryType = "solarOffgrid"; // Default to device load entry type

  // Create an event dispatcher
  const dispatch = createEventDispatcher();
  
  function generateDummyData() {
  const batteryCurrent = [];
  const batteryVoltage = [];
  const panelCurrent = [];
  const panelVoltage = [];
  const temp = [];
  const soc = [];
  const reductionFactor = 0.95; // 5% reduction for the second half

  // Helper function to simulate solar peak at 12:00
  function solarValue(index, peakValue) {
    // Convert index to time (6:00 - 18:00)
    const time = 6 + (index / 144) * 12;
    // Calculate the angle for the sine wave
    const angle = ((time - 6) / 12) * Math.PI;
    // Sine wave for peak at 12:00 and low at start/end of day
    return peakValue * Math.sin(angle);
  }

  // Function to generate data for each array
  function generateData(array, peakValue, isTemperature = false, useSolarValue = false) {
    for (let i = 0; i < 288; i++) {
      let value;
      if (useSolarValue) {
        // Use the solarValue function for solar-related data
        value = solarValue(i % 144, peakValue);
      } else {
        // Generate a time from 06:00 to 18:00 in 5-minute intervals
        const time = new Date();
        time.setHours(6, (i % 144) * 5, 0, 0);

        // Adjust the multiplier for randomness according to the time of the day
        const multiplier = (time.getHours() === 14) ? 0.1 : 0.5;

        // Generate dummy data with random fluctuations around the reference values
        value = peakValue + Math.random() * multiplier;
        if (isTemperature) {
          value += Math.random() * multiplier * 3; // Larger fluctuation for temperature
        }
      }
      if (i >= 144) {
        value *= reductionFactor; // Reduce the value for the second half
      }
      array.push(value);
    }
  }

  // Generate data for each array
  generateData(batteryCurrent, 0.28, false, true); // Apply solarValue for batteryCurrent
  generateData(batteryVoltage, 13.57);
  generateData(panelCurrent, 1.31, false, true); // Apply solarValue for panelCurrent
  generateData(panelVoltage, 12.39, false, true); // Apply solarValue for panelVoltage
  generateData(temp, 38, true);
  generateData(soc, 20, true);

  return { batteryCurrent, batteryVoltage, panelCurrent, panelVoltage, temp, soc };
}

function generateMonthlyDummyData() {
  const batteryCharge = [];
  const batteryDischarge = [];
  const powerProduction = [];
  const daysInMonth = 30; // Assuming 30 days for simplicity
  const halfSize = 31; // Half of 62
  const reductionFactor = 0.95; // 5% reduction for the second half

  // Assuming average daily peak values based on daily data
  const averageBatteryVoltage = 13.57;
  const averagePanelVoltage = 12.39;
  const averageBatteryCurrent = 0.28;
  const averagePanelCurrent = 1.31;

  // Function to generate monthly power data
  function generatePowerData(chargeArray, dischargeArray, productionArray) {
    for (let i = 0; i < 62; i++) {
      // Simulate the daily variation by using a random multiplier
      const dailyVariation = 1 + (Math.random() - 0.5) / 10; // +/- 5% daily variation

      // Calculate average daily power values
      const dailyChargePower = averageBatteryVoltage * averageBatteryCurrent * dailyVariation;
      const dailyDischargePower = dailyChargePower / 2; // Assuming discharge is half of charge
      const dailyProductionPower = averagePanelVoltage * averagePanelCurrent * dailyVariation;

      // Accumulate the daily values to get a monthly approximation
      let monthlyChargePower = dailyChargePower * daysInMonth;
      let monthlyDischargePower = dailyDischargePower * daysInMonth;
      let monthlyProductionPower = dailyProductionPower * daysInMonth;

      if (i >= halfSize) {
        // Apply reduction factor for the second half of the month
        monthlyChargePower *= reductionFactor;
        monthlyDischargePower *= reductionFactor;
        monthlyProductionPower *= reductionFactor;
      }

      chargeArray.push(monthlyChargePower);
      dischargeArray.push(monthlyDischargePower);
      productionArray.push(monthlyProductionPower);
    }
  }

  // Generate monthly power data for each array
  generatePowerData(batteryCharge, batteryDischarge, powerProduction);

  return { batteryCharge, batteryDischarge, powerProduction };
}



  // hour (start 00:00) = 2(odd even) x 24 Hour x 6 (10 mins interval) = 288 element
  // month (start odd month) = 2(odd even) x 31 Days (1 day interval) = 62 element
  let solarReading = {
    readings: {
      batteryCurrent: 0,
      batteryVoltage: 0,
      panelCurrent: 0,
      panelVoltage: 0,
	  temp: 0,
	  soc: 0
    },
    stats: {
      daily: {
        batteryCurrent: [],
        batteryVoltage: [],
        soc: [],
        panelCurrent: [],
        panelVoltage: [],
		temp: [],
      },
      monthly: {
        batteryCharge: [],
        batteryDischarge: [],
        powerProduction: [],
      },
      curveIV: {
        voltage: [],
        current: [],
      }
    },
  };

  Object.entries(solarReading.stats).forEach(([timespan,params]) => {
    let count = 100;
    if (timespan == "daily") count = 288;
    else if (timespan == "monthly") count = 62;
    Object.entries(params).forEach(([key,value]) => {
      for (let i = 0; i < count; ++i) {
      value.push(0);
      }
    solarReading.stats[timespan][key] = value 
    });

    // console.log(solarReading.stats[element[0]][Object.keys(element[1])[0]])
  });
  
  
 /*  solarReading.stats["daily"] = generateDummyData();
	solarReading.stats["monthly"] = generateMonthlyDummyData();
	console.log("dummy",solarReading.stats);  */
  
  let solarParams = {
    settings: {
      toggleUpdate: false,
	  toggleLoad: false,
	  toggleCutOff: false,
      emptyChargeVoltage: 11.36,
      fullChargeVoltage: 12.73,
      bulkCurrentMax: 2.25,
      floatVoltageMax: 13.6,
      absorbVoltageMax: 14.4,
	  absorbCurrentMax: 0.05,
	  tailscaleIP: "",
    },
  };

  // Form fields for different entry types
  const readingForm = {
    solarOffgrid: solarReading,
    solarOngrid: solarReading,
  };

  let formFields;

  // Function to save changes and emit an update event
  function saveChanges() {
    // Emit the 'update' event with the updated object and index
    dispatch("add", {
      updatedObj: Object.assign(
        {},
        formFields[entryType],
        readingForm[entryType]
      ),
    });
  }

  $: if ($mapCenter) {
    let solarDetails = {
      name: "",
      details: {
        lat: $mapCenter.lat,
        lng: $mapCenter.lng,
        type: "Solar",
        status: "normal",
        area: 2,
        azimuth: 1.2,
        altitude: 2,
        lastUpdate: 0,
      },
    };
    formFields = {
      solarOffgrid: Object.assign({}, solarParams, solarDetails),
      solarOngrid: Object.assign({}, solarParams, solarDetails),
    };
  }
</script>

<div class="add no-scrollbar">
  <select bind:value={entryType}>
    <option value="solarOffgrid">Solar Offgrid</option>
  </select>

  <!-- Dynamic form based on the selected entry type -->
  <form>
    <Child settings={formFields[entryType]} />
	<a
            href="?mode=Monitor"
            
          >
    <button type="submit" on:click={saveChanges}>Add</button>
	</a>
  </form>
</div>

<style>
  /* Style the add */
  .add {
    background-color: #fff;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    height: 100%;
    width: 96%;
    overflow-y: auto;
    margin: 2%;
  }

  div {
    font-family: Arial, sans-serif;
    margin: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f9f9f9;
    height: 100%;
    width: 100%;
  }

  button {
    padding: 5px 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }

  button:hover {
    background-color: #0056b3;
  }

  /* Styling for each property */
  div > div {
    margin: 10px 0;
  }

  strong {
    margin-right: 10px;
    font-weight: bold;
  }

  input[type="text"],
  input[type="number"] {
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 5px;
    max-width: 100%; /* Adjust this value based on your requirements */
    width: 100px;
    display: inline-block; /* Ensure elements are displayed in line */
  }

  span {
    padding: 5px;
  }

  /* remove scroll-bar */
  .no-scrollbar {
    scrollbar-width: none;
  }
  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }
</style>
