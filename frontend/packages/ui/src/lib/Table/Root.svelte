<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts" generics="T extends unknown">
  import { IconList } from "@intric/icons/list";
  import { IconSquares } from "@intric/icons/squares";
  import { writable } from "svelte/store";
  import type { ComponentType, SvelteComponent } from "svelte";
  import { Button, Input } from "$lib/index.js";
  import { Subscribe, Render } from "svelte-headless-table";
  import { getCardCell, setTableContext, type ResourceTableViewModel } from "./create.js";
  import SortButton from "./SortButton.svelte";
  import Group from "./Group.svelte";
  import EmptyState from "./EmptyState.svelte";
  import { cva } from "class-variance-authority";

  export let displayAs: "cards" | "list" = "list";
  const displayType = writable<"cards" | "list">(displayAs);

  /** Vertical gap in `rem` in grid layout */
  export let gapX: string | number = "2";
  /** Horizontal gap in `rem` in grid layout */
  export let gapY: string | number = "2";
  export let layout: "flex" | "grid" = "flex";
  /** Use this option if the table is used within a clearly outlined area;
   * It will add symmetric padding to the filter bar and add a slight internal shadow
   */
  export let fitted = false;

  export let filter: boolean = true;
  export let viewModel: ResourceTableViewModel<T>;

  export let resourceName = "item";
  /**
   * Left padding of action column, in big tables this can be left as is.
   * If the table is in a thight place you can set this to tight to free up some space
   */
  export let actionPadding: "regular" | "tight" = "regular";

  export let emptyMessage: string | undefined = undefined;
  export let emptyIcon:
    | ComponentType<SvelteComponent<{ size?: "small" | "base" | "large"; class?: string }>>
    | undefined = undefined;

  setTableContext({
    displayType,
    viewModel,
    gapX,
    gapY,
    layout
  });

  const { headerRows, pageRows: rows, tableAttrs } = viewModel;
  const { filterValue } = viewModel.pluginStates.tableFilter;
  const showCardSwitch = getCardCell($rows[0]) !== undefined;

  const filterContainer = cva("flex items-center justify-between gap-4 pb-1 pr-3 pt-3.5", {
    variants: {
      fitted: {
        true: "pl-3",
        false: null
      }
    },
    defaultVariants: {
      fitted: false
    }
  });

  const tableHeader = cva("h-14 border-b border-default px-2 text-left font-medium", {
    variants: {
      action: {
        true: "w-[1%]",
        false: "w-[10%]"
      }
    },
    defaultVariants: {
      action: false
    }
  });
</script>

<div class="flex w-full flex-col">
  <div class={filterContainer({ fitted })}>
    {#if filter}
      <Input.Text
        bind:value={$filterValue}
        label="Filter"
        class="flex-grow"
        placeholder={`Filter ${resourceName}s...`}
        hiddenLabel={true}
        inputClass="!px-4"
      ></Input.Text>
    {/if}

    <div class="flex justify-stretch gap-1 rounded-xl">
      <Button
        on:click={() => {
          $displayType = "list";
        }}
        displayActiveState
        data-state={$displayType === "list" ? "active" : ""}
        padding="icon-leading"
      >
        <IconList />
        List
      </Button>
      {#if showCardSwitch}
        <Button
          padding="icon-leading"
          on:click={() => {
            $displayType = "cards";
          }}
          displayActiveState
          data-state={$displayType === "cards" ? "active" : ""}
        >
          <IconSquares />
          Cards
        </Button>
      {/if}
    </div>
  </div>
  <div class="w-full">
    {#if $rows.length > 0}
      {#if $displayType === "list"}
        <table {...$tableAttrs} class="w-full border-separate border-spacing-0">
          <thead class="bg-frosted-glass-primary sticky top-0 z-30">
            {#each $headerRows as headerRow (headerRow.id)}
              <Subscribe rowAttrs={headerRow.attrs()} let:rowAttrs>
                <tr {...rowAttrs}>
                  {#each headerRow.cells as cell (cell.id)}
                    {#if cell.id !== "table-card-key"}
                      <Subscribe attrs={cell.attrs()} let:attrs>
                        <th
                          {...attrs}
                          class={tableHeader({ action: cell.id === "table-action-key" })}
                        >
                          <SortButton
                            props={cell.props()}
                            actionPadding={cell.id === "table-action-key"
                              ? actionPadding
                              : undefined}
                          >
                            <Render of={cell.render()} />
                          </SortButton>
                        </th>
                      </Subscribe>
                    {/if}
                  {/each}
                </tr>
              </Subscribe>
            {/each}
          </thead>
          <slot>
            <Group />
          </slot>
        </table>
      {:else}
        <div class="card-container">
          <slot>
            <Group />
          </slot>
        </div>
      {/if}
    {:else}
      <div
        class="pointer-events-none absolute inset-0 flex min-h-[500px] items-center justify-center"
      >
        <EmptyState filterValue={$filterValue} {resourceName} {emptyMessage} {emptyIcon} />
      </div>
    {/if}
  </div>
</div>
