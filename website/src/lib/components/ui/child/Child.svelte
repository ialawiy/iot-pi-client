<!-- Child.svelte -->
<script>
  import { onMount } from "svelte";
  import Child from "./Child.svelte"; // Make sure the path is correct
  import { mode, valueChange } from "$lib/store/store";

  let initialSettings;

  export let settings = {}; // This is the original object from the parent component

  export let parent = ""; // This is the original object from the parent component
  let inputType = "number";

  

  onMount(() => {
    // Initialize initialSettings with a copy of settings
    if (settings) initialSettings = JSON.parse(JSON.stringify(settings));
    // console.log("set",settings)
    // // console.log(settings);
  });

  // Function to convert camelCase to Sentence case
  function toSentenceCase(str) {
    return str.replace(/([A-Z])/g, " $1").replace(/^./, function (str) {
      return str.toUpperCase();
    });
  }
  
  function getUnitFromString(inputString) {
	  // console.log("inputString",inputString)
	  const units = {
		'voltage': 'V', // Volts
		'current': 'A', // Amperes
		'temp': '°C', // Degrees Celsius
		// Add more keywords and units as needed
	  };

	  // Convert camelCase to lower case with spaces for easier keyword detection
	  const lowerCaseString = inputString.replace(/([A-Z])/g, ' $1').toLowerCase();

	  for (let key in units) {
		if (lowerCaseString.includes(key)) {
		  return units[key];
		}
	  }

	  return ''; // Return an empty string if no unit keyword is detected
	}

  // Function to display keys in Sentence case
  function displayKey(key) {
    return toSentenceCase(key);
  }

  // Function to determine the type of a value
  function getValueType(value) {
    if (typeof value === "boolean") {
      return "boolean";
    } else if (typeof value === "number") {
      return "number";
    } else if (typeof value === "string") {
      return "string";
    } else {
      return "unknown";
    }
  }

  // Function to format "onTime" values as "hh:mm - hh:mm"
  function formatOnTime(value) {
    if (
      typeof value === "object" &&
      value.hasOwnProperty("startHour") &&
      value.hasOwnProperty("endHour") &&
      value.hasOwnProperty("startMinutes") &&
      value.hasOwnProperty("endMinutes")
    ) {
      return `${value.startHour}:${value.startMinutes} - ${value.endHour}:${value.endMinutes}`;
    } else {
      return value;
    }
  }

  // Function to format "onTime" values as "hh:mm - hh:mm"
  function formatLimit(value) {
    if (
      typeof value === "object" &&
      value.hasOwnProperty("min") &&
      value.hasOwnProperty("max")
    ) {
      return `${value.min} - ${value.max}`;
    } else {
      return value;
    }
  }

  // Function to parse "onTime" string back to object format
  function parseOnTime(value) {
    const [start, end] = value.split(" - ");
    const [startHour, startMinutes] = start.split(":");
    const [endHour, endMinutes] = end.split(":");
    return {
      startHour: Number(startHour),
      startMinutes: Number(startMinutes),
      endHour: Number(endHour),
      endMinutes: Number(endMinutes),
    };
  }

  function updateOriginalObject(key, newValue) {
    if (key === "onTime") {
      // Handle onTime separately by parsing the edited string
      settings[key] = newValue ? parseOnTime(newValue) : null;
      // console.log("onTime", settings[key]);
    } else if (typeof newValue === "boolean") {
      settings[key] = newValue === "" ? "" : newValue;
    } else {
      const keys = key.split(".");
      let currentObj = settings;
      for (let i = 0; i < keys.length - 1; i++) {
        currentObj = currentObj[keys[i]];
      }
      const lastKey = keys[keys.length - 1];
      currentObj[lastKey] = newValue;
      // console.log(currentObj, settings);
    }
  }

  // Function to determine if a value has been edited and is different from the original
  function isValueChanged(key) {
    //return $mode && settings[key] !== initialSettings[key];
    if (initialSettings && $mode)
      return (
        JSON.stringify(settings[key]) !== JSON.stringify(initialSettings[key])
      );
    else initialSettings = settings;
  }
</script>
<div class="readings parent">
{#if settings.readings}
{#each Object.entries(settings.readings) as [key, value]}
{#if !["temp", "soc"].includes(key)}
<div class="reading-child">
<p>{displayKey(key)}</p>
  <p >{value + getUnitFromString(key)}</p>
</div>
{/if}
{/each}

{/if}
</div>
{#each Object.entries(settings) as [key, value]}
  {#if !["id", "stats", "type", "readings"].includes(key)}
    {#if  !(key == "name" && $mode != 'Add')}
    <div class={typeof value === "object"  ? "parent" : "child"}>
      <p>{displayKey(key)}</p>
      {#if typeof value === "object" && value !== null}
        <!-- Recursive call for nested objects -->
        <div class="child">
          <Child bind:settings={value} parent={key} style="display: subgrid;" />
        </div>
      {:else if parent == "readings"}
        <span>{value}</span>
      {:else if getValueType(value) === "boolean"}
        <button on:click={() => updateOriginalObject(key, !settings[key])}>
          {settings[key] ? "ON" : "OFF"}
        </button>
      {:else if getValueType(value) === "numeric"}
        <input type="number" bind:value={settings[key]} />
		<span class="unit">{getUnitFromString(settings[key])}</span>
      {:else}
        <input bind:value={settings[key]} />
      {/if}
      {#if isValueChanged(key)}
        <span>*</span> <!-- Display '*' for edited and different values -->
      {/if}
    </div>
    {/if}
    {/if}
{/each}

<style>
  /* Styling for the entire component */
  div {
  }
  p {
    font-size: 0.8rem;
    color:  var(--font);
  }
  .parent {
    font-family: Arial, sans-serif;
    margin: 5px;
    padding-left: 5px;
    border-left: 2px solid var(--border);
    background-color: var(--primary);
    width: 45%; /* Adjust this value based on your requirements */
    max-height: 100%; /* Adjust this value based on your requirements */
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
  }
  .readings{
  width: 100%;
  font-size: 1rem;
  border-left: unset;
  }
  .reading-child{
    display: flex;
    flex-direction: column;
  width: 25%;
  

  }
  .reading-child p{
    font-size: min(0.8rem,1.5vw);
  }
  .child {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
  
  .unit {
    position: absolute;
    right: 10px;
    top: 0;
    bottom: 0;
    height: 20px;
    margin: auto;
    pointer-events: none;
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
    margin: 3px 0;
  }

  strong {
    margin-right: 10px;
    font-weight: bold;
  }

  input {
    border-bottom: 1px solid #ccc;
    border-radius: 5px;
    padding: 5px;
    display: inline-block; /* Ensure elements are displayed in line */
  }

  span {
    padding: 0px;
  }

  @media (max-width: 600px) {
    input[type="text"],
    input[type="numeric"] {
      border-left: 1px solid #ccc;
      padding: 0px;
      padding-left: 2px;
      display: inline-block; /* Ensure elements are displayed in line */
    }

    input {
      width: auto;
    }

    .reading-child p{
    font-size: max(0.7rem,1.5vw);
  }
  }
</style>
