<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager";
  import type { TranscriptionModel } from "@intric/intric-js";
  import ModelNameAndVendor from "$lib/features/ai-models/components/ModelNameAndVendor.svelte";
  import { Input, Tooltip } from "@intric/ui";
  import { derived } from "svelte/store";
  import { Settings } from "$lib/components/layout";
  import { sortModels } from "$lib/features/ai-models/sortModels";

  export let selectableModels: (TranscriptionModel & {
    meets_security_classification?: boolean | null | undefined;
  })[];
  sortModels(selectableModels);

  const {
    state: { currentSpace },
    updateSpace
  } = getSpacesManager();

  const currentlySelectedModels = derived(
    currentSpace,
    ($currentSpace) => $currentSpace.transcription_models.map((model) => model.id) ?? []
  );

  let loading = new Set<string>();
  async function toggleModel(model: TranscriptionModel) {
    loading.add(model.id);
    loading = loading;

    try {
      if ($currentlySelectedModels.includes(model.id)) {
        const newModels = $currentlySelectedModels
          .filter((id) => id !== model.id)
          .map((id) => {
            return { id };
          });
        await updateSpace({ transcription_models: newModels });
      } else {
        const newModels = [...$currentlySelectedModels, model.id].map((id) => {
          return { id };
        });
        await updateSpace({ transcription_models: newModels });
      }
    } catch (e) {
      alert(e);
    }
    loading.delete(model.id);
    loading = loading;
  }
</script>

<Settings.Row
  title="Transcription Models"
  description="Choose which transcription models will be available to transcribe audio in this space."
>
  <svelte:fragment slot="description">
    {#if $currentSpace.transcription_models.length === 0}
      <p
        class="label-warning border-label-default bg-label-dimmer text-label-stronger mt-2.5 rounded-md border px-2 py-1 text-sm"
      >
        <span class="font-bold">Hint:&nbsp;</span>Enable a transcription model to be able to process
        audio in this space.
      </p>
    {/if}
  </svelte:fragment>

  {#each selectableModels as model (model.id)}
    {@const meetsClassification = model.meets_security_classification ?? true}
    <Tooltip
      text={meetsClassification
        ? undefined
        : "This model does not meet the selected security classification"}
    >
      <div
        class="border-default hover:bg-hover-dimmer cursor-pointer border-b py-4 pr-4 pl-2"
        class:pointer-events-none={!meetsClassification}
        class:opacity-60={!meetsClassification}
      >
        <Input.Switch
          value={$currentlySelectedModels.includes(model.id)}
          sideEffect={() => {
            if (meetsClassification) {
              toggleModel(model);
            }
          }}
        >
          <ModelNameAndVendor {model} />
        </Input.Switch>
      </div>
    </Tooltip>
  {/each}
</Settings.Row>
