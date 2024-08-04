<script>
    import * as Accordion from "$lib/components/ui/accordion/index.js";
  import * as Resizable from "$lib/components/ui/resizable/index.js";
  import { toggleMode } from "mode-watcher";
  import * as Carousel from "$lib/components/ui/carousel/index.js";
  import Authenticate from "$lib/components/ui/auth/Authenticate.svelte";
  </script>
  <Authenticate />
<!-- <div> 
  <Accordion.Root class="w-full sm:max-w-[70%]">
    <Accordion.Item value="item-1">
      <Accordion.Trigger>Is it accessible?</Accordion.Trigger>
      <Accordion.Content
        >Yes. It adheres to the WAI-ARIA design pattern.</Accordion.Content
      >
    </Accordion.Item>
    <Accordion.Item value="item-2">
      <Accordion.Trigger>Is it styled?</Accordion.Trigger>
      <Accordion.Content>
        Yes. It comes with default styles that matches the other components'
        aesthetic.
      </Accordion.Content>
    </Accordion.Item>
    <Accordion.Item value="item-3">
      <Accordion.Trigger>Is it animated?</Accordion.Trigger>
      <Accordion.Content>
        Yes. It's animated by default, but you can disable it if you prefer.
      </Accordion.Content>
    </Accordion.Item>
  </Accordion.Root>

</div>  
<div>  

</div>  
<div><Resizable.PaneGroup direction="horizontal" class="max-w-md rounded-lg border">
    <Resizable.Pane defaultSize={50}>
      <div class="flex h-[200px] items-center justify-center p-6">
        <span class="font-semibold">One</span>
      </div>
    </Resizable.Pane>
    <Resizable.Handle />
    <Resizable.Pane defaultSize={50}>
      <Resizable.PaneGroup direction="vertical">
        <Resizable.Pane defaultSize={25}>
          <div class="flex h-full items-center justify-center p-6">
            <span class="font-semibold">Two</span>
          </div>
        </Resizable.Pane>
        <Resizable.Handle />
        <Resizable.Pane defaultSize={75}>
          <div class="flex h-full items-center justify-center p-6">
            <span class="font-semibold">Three</span>
          </div>
        </Resizable.Pane>
      </Resizable.PaneGroup>
    </Resizable.Pane>
  </Resizable.PaneGroup>
</div>
<div><Button on:click={toggleMode} variant="outline" size="icon">
    p
    <span class="sr-only">Toggle theme</span>
  </Button>
</div>
<div>
<Carousel.Root class="w-full max-w-xs">
    <Carousel.Content>
      {#each Array(5) as _, i (i)}
        <Carousel.Item>
          <div class="p-1">
            <Card.Root>
              <Card.Content
                class="flex aspect-square items-center justify-center p-6"
              >
                <span class="text-4xl font-semibold">{i + 1}</span>
              </Card.Content>
            </Card.Root>
          </div>
        </Carousel.Item>
      {/each}
    </Carousel.Content>
    <Carousel.Previous />
    <Carousel.Next />
  </Carousel.Root>
</div> -->