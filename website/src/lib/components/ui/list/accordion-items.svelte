<script>
  import { getAccordionOptions } from "./context";

  // get the accordion options using the context api
  const { collapse, activeComponentId } = getAccordionOptions();

  import { selected, mode } from "$lib/store/store";

  // by default the accordion item is closed
  export let open = false;

  export let order;

  function setActive() {
    // update the store value in the context
    //$activeComponentId = componentId
    $activeComponentId = isActive ? false : order;
    $selected = $activeComponentId;
  }

  $: $activeComponentId = $selected;

  function toggleOpen() {
    open = !open;
    
  }
  function handleClick() {
    // if `collapse` is passed only one item can be active
    //$isOpen = !$isOpen
    collapse ? setActive() : toggleOpen();
    // console.log(collapse, $activeComponentId);
    isOpen = isActive ? !isOpen : isActive;
    // const link = document.getElementById("item-content");
    // console.log(isActive)
    // if (isActive) link.classList.remove("hide");
    // else link.classList.add("hide");
  }
  // the accordion item to be open by default
  $: open && collapse && setActive();
  // compare if the active id matches the component id
  $: isActive = $activeComponentId === order;
  // if `collapse`, set one item as active, otherwise use `open`
  $: isOpen = collapse ? isActive : open;

</script>

{#if isActive || $selected == false}
  <div class="item no-scrollbar">
    <div class="toggle">
      <div class="title">
        <slot name="title" />
      </div>
      <div on:click={handleClick} class="caret">
        <i class='bx bxs-chevrons-{isOpen ? 'up' : 'down'}'></i>
      </div>
    </div>
    <div class="content {!isOpen && ($mode == 'Monitor' ) ? 'preview' : ''}" >
      <slot name="content" id="item-content"/>
    </div>
  </div>
{/if}

<style>
  .toggle {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: var(--padding, 12px);
    font: inherit;
    font-weight: 600;
    border: none;
    background: none;
    cursor: pointer;
    border-radius: var(--radius, 4px);
    transition: background-color 0.1s ease;
  }

  .preview {
    height : 50px;
  }

  .hide {
    display:none;
  }

  .item:hover {
    box-shadow: 0px 0px 2px 1px var(--secondary);
  }

  .content {
    padding: var(--content-padding, 0px);
  }

  .title {
	display:flex;
	flex-direction:row;
    width: 100%;
  }

  .item {
    height: 100%;
    overflow-y: auto;
    border-radius: 12px;
    margin: 2px 2px 15px 2px;
    box-shadow: 0px 0px 1px 1px lightgray;
  }

  /* remove scroll-bar */
  .no-scrollbar {
    scrollbar-width: none;
  }

  @media (max-width: 600px) {
    .preview {
    height : 45px;
  }
  }
</style>
