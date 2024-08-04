<script>
  import { userAuth } from "$lib/store/store";
  
      import * as Tabs from "$lib/components/ui/tabs/index.js";
  import * as Card from "$lib/components/ui/card/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Label } from "$lib/components/ui/label/index.js";
  

  let email = "";
  let password = "";
  let confirmPass = "";
  let errorMessage;
  let error = false;
  let register = false;
  let authenticating = false;

  async function handleAuthenticate() {
    if (authenticating) {
      return;
    }
    if (!email || !password || (register && !confirmPass)) {
      error = true;
      return;
    }
    authenticating = true;

    try {
      if (!register) {
        await userAuth.login(email, password);
      } else {
        await userAuth.signup(email, password);
      }
    } catch (err) {
      console.log("There was an auth error", err);
	  errorMessage = err;
      error = true;
      authenticating = false;
    }
  }

  function handleRegister() {
    register = !register;
	console.log("regis",register)
  }
  function handlePublic() {
    email = 'public@user.com';
    password = '11111111'
    register = false;
    handleAuthenticate()
  }
</script>


<div class="w-full h-full lg:grid lg:min-h-[600px] lg:grid-cols-2 ">
  <div class="flex items-center justify-center py-12">
    <div class="mx-auto grid w-[350px] gap-6">
      <Tabs.Root value="sign-in" class="sm:w-[400px] w-full ">
    <Tabs.List class="grid w-full grid-cols-2">
      <Tabs.Trigger value="sign-in" on:click={handleRegister}>Login</Tabs.Trigger>
      <Tabs.Trigger value="sign-up" on:click={handleRegister}>Register</Tabs.Trigger>
    </Tabs.List>
    {#if error}
      <p class="error">The information you have entered is not correct</p>
		<p class="error">{errorMessage}</p>
    
	{/if}
    <Tabs.Content value="sign-in">
      <Card.Root>
        <Card.Header>
          <Card.Title>Enter Credentials</Card.Title>
          <Card.Description>
            Make changes to your account here. Click save when you're done.
          </Card.Description>
        </Card.Header>
        <Card.Content class="space-y-2">
          <div class="space-y-1">
            <Label for="email">Email</Label>
            <Input id="email" bind:value={email} />
          </div>
          <div class="space-y-1">
            <Label for="pass">Password</Label>
            <Input id="pass" type="password" bind:value={password} />
          </div>
        </Card.Content>
        <Card.Footer class="grid gap-2">
          <Button on:click={handleAuthenticate}  class="w-full">{#if authenticating}
            <i class="fa-solid fa-spinner loadingSpinner" />
          {:else}
            Login
          {/if}</Button>
          <Button on:click={handlePublic} variant="outline" class="w-full">{#if authenticating}
            <i class="fa-solid fa-spinner loadingSpinner" />
          {:else}
            Public Account
          {/if}</Button>
        </Card.Footer>
      </Card.Root>
    </Tabs.Content>
    <Tabs.Content value="sign-up">
      <Card.Root>
        <Card.Header>
          <Card.Title>Create New Account</Card.Title>
          <Card.Description>
            Enter details to your new account here. Click save when you're done.
          </Card.Description>
        </Card.Header>
        <Card.Content class="space-y-2">
          <div class="space-y-1">
            <Label for="email">Email</Label>
            <Input id="email" bind:value={email} />
          </div>
          <div class="space-y-1">
            <Label for="pass">Password</Label>
            <Input id="pass" bind:value={password} />
          </div>
          <div class="space-y-1">
            <Label for="confirm-pass">Confirm Password</Label>
            <Input id="confirm-pass" bind:value={confirmPass} />
          </div>
        </Card.Content>
        <Card.Footer>
          <Button on:click={handleAuthenticate} class="w-full">{#if authenticating}
            <i class="fa-solid fa-spinner loadingSpinner" />
          {:else}
            Create Account
          {/if}</Button>
        </Card.Footer>
      </Card.Root>
    </Tabs.Content>
  </Tabs.Root>
    </div>
  </div>
  <div class="hidden bg-muted lg:block">
    <img
      src="/auth-img.webp"
      alt="placeholder"
      height="100%"
      class="h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
    />
  </div>
</div>


<div class="authContainer">
  
  <!-- <form>
    <h1>{register ? "Register" : "Login"}</h1>
    {#if error}
      <p class="error">The information you have entered is not correct</p>
    {/if}
    <label>
      <p class={email ? " above" : " center"}>Email</p>
      <input bind:value={email} type="email" placeholder="Email" />
    </label>
    <label>
      <p class={password ? " above" : " center"}>Password</p>
      <input bind:value={password} type="password" placeholder="Password" />
    </label>
    {#if register}
      <label>
        <p class={confirmPass ? " above" : " center"}>Confirm Password</p>
        <input bind:value={confirmPass} type="password" placeholder="Confirm Password" />
      </label>
    {/if}

    <button on:click={handleAuthenticate} type="button" class="submitBtn">
      {#if authenticating}
        <i class="fa-solid fa-spinner loadingSpinner" />
      {:else}
        Submit
      {/if}
    </button>
  </form>
  <div class="options">
    <p>Or</p>
    {#if register}
      <div>
        <p>Already have an account?</p>
        <p on:click={handleRegister} on:keydown={() => {}}>Login</p>
      </div>
    {:else}
      <div>
        <p>Don't have an account?</p>
        <p on:click={handleRegister} on:keydown={() => {}}>Register</p>
      </div>
      <div>
        <p>Or use</p>
        <p on:click={handlePublic} on:keydown={() => {}}>Public Account</p>
      </div>
    {/if}
  </div> -->
</div>

<style>
  .authContainer {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    padding: 24px;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  form,
  .options {
    width: 400px;
    max-width: 100%;
    margin: 0 auto;
  }

  form input {
    width: 100%;
  }

  h1 {
    text-align: center;
    font-size: 3rem;
  }

  form label {
    position: relative;
    border: 1px solid #555555;
    border-radius: 5px;
  }

  form input {
    border: none;
    background: transparent;
    color: #594545;
    padding: 14px;
  }

  form input:focus {
    border: none;
    outline: none;
  }

  form label:focus-within {
    border-color: #111111;
  }

  form button {
    background: #555555;
    color: white;
    border: none;
    padding: 14px 0;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    display: grid;
    place-items: center;
  }

  form button:hover {
    opacity: 0.7;
  }

  .above,
  .center {
    position: absolute;
    transform: translateY(-50%);
    pointer-events: none;
    color: white;
    border-radius: 4px;
    padding: 0 6px;
    font-size: 0.8rem;
  }

  .above {
    top: 0;
    left: 24px;
    background: #555555;
    border: 1px solid #594545;
    font-size: 0.7rem;
  }

  .center {
    top: 50%;
    left: 6px;
    border: 1px solid transparent;
    opacity: 0;
  }

  .error {
    color: coral;
    font-size: 0.9rem;
    text-align: center;
  }

  .options {
    padding: 14px 0;
    overflow: hidden;
    font-size: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .options > p {
    position: relative;
    text-align: center;
    width: fit-content;
    margin: 0 auto;
    padding: 0 8px;
  }

  .options > p::after,
  .options > p::before {
    position: absolute;
    content: "";
    top: 50%;
    transform: translateY(-50%);
    width: 100vw;
    height: 1.5px;
    background: white;
  }

  .options > p::after {
    right: 100%;
  }

  .options > p::before {
    left: 100%;
  }

  .options div {
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: center;
  }

  .options div p:last-of-type {
    color: #111111;
    cursor: pointer;
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
</style>

