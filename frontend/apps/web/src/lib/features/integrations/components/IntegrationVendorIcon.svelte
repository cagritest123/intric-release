<script lang="ts">
  import { cva } from "class-variance-authority";
  import { integrationData, type IntegrationType } from "../IntegrationData";

  type Props = {
    size: "sm" | "lg";
    type?: IntegrationType;
  };

  const { size, type = "confluence" }: Props = $props();
  const logoUrl = $derived.by(() => {
    return integrationData[type].logo;
  });

  const image = cva(null, {
    variants: {
      size: {
        sm: ["w-6"],
        lg: ["w-12"]
      }
    }
  });
</script>

<img src={logoUrl} alt="" class={image({ size })} />
