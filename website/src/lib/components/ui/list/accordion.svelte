<script>
  // by default more than one accordion can be open
  import { setAccordionOptions } from "./context";
  export let collapse = false;
  // the context API avoids passing data through components as props
  setAccordionOptions({ collapse });
</script>

<div class="accordion">
  <slot />
</div>

<style>
  .accordion {
    width: var(--width, 100%);
	overflow:auto;
	display: flex;
	
    flex-direction: column;
    padding: var(--padding, 0);
    border-radius: var(--radius, 4px);
	  justify-content: space-between; /* Align children at the start and end */

  }
</style>
