<!-- BASED ON MIT LICENSED CODE FROM https://github.com/prgm-dev/sveltekit-progress-bar -->

<!--
  @component

  A Progress Bar that hooks to SvelteKit navigation.

  The progress bar will show during navigation if loading takes more than `displayThresholdMs`
  and will hide when navigation is complete.
-->
<script lang="ts">
  import { afterNavigate, beforeNavigate } from "$app/navigation";

  // This component is a modified version of the component from the following repo:
  // https://github.com/saibotsivad/svelte-progress-bar

  // Towards the end of the progress bar animation, we want to shorten the increment
  // step size, to give it the appearance of slowing down. This indicates to the user
  // that progress is still happening, but not as fast as they might like.
  const getIncrement = (n: number) => {
    if (n >= 0 && n < 0.2) return 0.1;
    else if (n >= 0.2 && n < 0.5) return 0.04;
    else if (n >= 0.5 && n < 0.8) return 0.02;
    else if (n >= 0.8 && n < 0.99) return 0.005;
    return 0;
  };

  // Internal private state.
  let running: boolean = false;
  let updater: ReturnType<typeof setInterval> | null = null;
  let completed = false;
  let width: number = 0;

  /** If set, an ID for the progress bar on the HTML page.
   * This ID must be unique on the page to avoid conflicts.
   *
   * Might be used with another element to signal to assistive technologies that
   * progress is ongoing.
   *
   * @example
   * <ProgressBar id="my-progress-bar" bind:busy />
   * <div aria-busy={busy} aria-describedby="my-progress-bar">
   *  A div that is currently loading...
   * </div>
   */
  export let id: string | undefined = undefined;
  /** Will be set to true when the progress bar is running. */
  export let busy: boolean = false;
  $: running = busy;
  /**
   * The CSS color to use to style the progress bar.
   *
   * If you're using Tailwind or Windi CSS, leave this to the default
   * and set the `class` attribute to a `text-` class instead.
   */
  export let color: string = "currentColor";
  /**
   * A Tailwind/Windi `text-` class to use to color the Progress Bar.
   *
   * This prop will be ignored if the `color` prop is set to something other than `currentColor`.
   *
   * **WARNING**: Do not set this prop with something other than a `text-` class,
   *              as it could interfere with the styling of the Progress Bar.
   *
   * @example text-green-500
   */
  let textColorClass: `text-${string}` | "" = "";
  export { textColorClass as class };

  /**
   * The `z-index` CSS property value to use for the progress bar.
   * Be aware that the glowing effect on the bar will use this `zIndex` + 1.
   */
  export let zIndex: number = 1;

  // These are defaults that you shouldn't need to change, but are exposed here in case you do.
  /**
   * The starting percent width use when the bar starts.
   * Starting at 0 doesn't usually look very good.
   * @default 0.08
   */
  let defaultMinimum = 0.08;
  export { defaultMinimum as minimum };
  /**
   * The maximum percent width value to use when the bar is at the end but not marked as complete.
   * Letting the bar stay at 100% width for a while doesn't usually look very good either.
   * @default 0.994
   */
  export let maximum = 0.994;
  /**
   * Milliseconds to wait after the complete method is called to hide the progress bar.
   * Letting it sit at 100% width for a very short time makes it feel more fluid.
   * @default 700
   */
  let defaultSettleTime = 700;
  export { defaultSettleTime as settleTime };
  /**
   * Milliseconds to wait between incrementing bar width when using
   * the `start` (auto-increment) method.
   * @default 700
   */
  export let intervalTime = 700;
  export let stepSizes = [0, 0.005, 0.01, 0.02];

  /** Reset the progress bar back to the beginning, leaving it in a running state. */
  export const reset = (minimum = defaultMinimum) => {
    width = minimum;
    running = true;
  };

  /**
   * Continue the animation of the progress bar from whatever position it is in, using
   * a randomized step size to increment.
   */
  export const animate = () => {
    if (updater) {
      // prevent multiple intervals by clearing before making
      clearInterval(updater);
    }
    running = true;
    updater = setInterval(() => {
      const randomStep = stepSizes[Math.floor(Math.random() * stepSizes.length)] ?? 0;
      const step = getIncrement(width) + randomStep;
      if (width < maximum) {
        width = width + step;
      }
      if (width > maximum) {
        width = maximum;
        stop();
      }
    }, intervalTime);
  };

  /** Restart the bar at the minimum, and begin the auto-increment progress. */
  export const start = (minimum?: number) => {
    reset(minimum);
    animate();
  };

  /** Stop the progress bar from incrementing, but leave it visible. */
  export const stop = () => {
    if (updater) {
      clearInterval(updater);
    }
  };

  /**
   * Moves the progress bar to the fully completed position, wait an appropriate
   * amount of time so the user can feel the completion, then hide and reset.
   */
  export const complete = (settleTime = defaultSettleTime) => {
    if (updater) clearInterval(updater);
    if (!running) return;
    width = 1;
    running = false;
    setTimeout(() => {
      // complete the bar first
      completed = true;
      setTimeout(() => {
        // after some time (long enough to finish the hide animation) reset it back to 0
        completed = false;
        width = 0;
      }, settleTime);
    }, settleTime);
  };

  /** Stop the auto-increment functionality and manually set the width of the progress bar. */
  export const setWidthRatio = (widthRatio: typeof width) => {
    stop();
    width = widthRatio;
    completed = false;
    running = true;
  };

  // Primarily used for tests, but can also be used for external monitoring.
  export const getState = () => {
    return {
      width,
      running,
      completed,
      color,
      defaultMinimum,
      maximum,
      defaultSettleTime,
      intervalTime,
      stepSizes
    };
  };

  let barStyle: string;
  $: barStyle =
    (color ? `background-color: ${color};` : "") +
    (width && width * 100 ? `width: ${width * 100}%;` : "") +
    `z-index: ${zIndex};`;
  // the box shadow of the leader bar uses `color` to set its shadow color
  let leaderColorStyle: string;
  $: leaderColorStyle =
    (color ? `background-color: ${color}; color: ${color};` : "") + `z-index: ${zIndex + 1};`;

  /** When navigating, this is the threshold duration in milliseconds
   * that the progress bar will wait before showing.
   *
   * This means that if the navigation takes less than this amount of time,
   * the progress bar will not be shown. This is to prevent the progress bar
   * from flashing in and out on the screen.
   *
   * @default 150 ms
   */
  export let displayThresholdMs = 150;

  /** Set to `true` to disable the showing of the progress bar on navigation. */
  export let noNavigationProgress = false;

  let progressBarStartTimeout: ReturnType<typeof setTimeout> | null = null;
  beforeNavigate((nav) => {
    if (progressBarStartTimeout) {
      clearTimeout(progressBarStartTimeout);
      progressBarStartTimeout = null;
    }
    if (noNavigationProgress) return;

    if (nav.to?.route.id) {
      // Internal navigation.
      if (displayThresholdMs > 0) {
        // Schedule a display of the progress bar in `displayThresholdMs` milliseconds.
        // This is to avoid flickering/flashing when the navigation is fast.
        progressBarStartTimeout = setTimeout(
          () => !noNavigationProgress && start(),
          displayThresholdMs
        );
      } else start();
    }

    nav.complete.finally(() => {
      if (progressBarStartTimeout) {
        clearTimeout(progressBarStartTimeout);
        progressBarStartTimeout = null;
      }
      complete();
    });
  });

  afterNavigate(() => {
    if (progressBarStartTimeout) {
      clearTimeout(progressBarStartTimeout);
      progressBarStartTimeout = null;
    }
    complete();
  });
</script>

{#if running || width > 0}
  <output
    {id}
    role="progressbar"
    aria-valuenow={width}
    aria-valuemin={0}
    aria-valuemax={1}
    class="svelte-progress-bar {textColorClass}"
    class:running
    class:svelte-progress-bar-hiding={completed}
    style={barStyle}
  >
    {#if running}
      <div class="svelte-progress-bar-leader" style={leaderColorStyle}></div>
    {/if}
  </output>
{/if}

<style>
  .svelte-progress-bar {
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    transition: width 0.21s ease-in-out;
  }

  .svelte-progress-bar-hiding {
    transition: top 0.8s ease;
    top: -8px;
  }

  .svelte-progress-bar-leader {
    position: absolute;
    top: 0;
    right: 0;
    height: 5px;
    width: 100px;
    transform: rotate(2.5deg) translate(0px, -4px);
    box-shadow: 0 0 8px;
  }
</style>
