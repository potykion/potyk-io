<script setup lang="ts">
import { computed } from "vue";
import type { RestRestaurant } from "@/api/rest";

const TIERS = ["S", "A", "B", "C", "D"] as const;

const props = defineProps<{
  items: RestRestaurant[];
  label?: string;
}>();

const byTier = computed(() => {
  const map: Record<string, RestRestaurant[]> = Object.fromEntries(
    TIERS.map((t) => [t, [] as RestRestaurant[]]),
  );
  for (const item of props.items) {
    const tier = String(item.tier || "").toUpperCase();
    if (!(tier in map)) continue;
    map[tier].push(item);
  }
  return map;
});

function hrefFor(item: RestRestaurant): string {
  return item.maps_url || "#";
}
</script>

<template>
  <table class="tier-list" :aria-label="label || 'Тирлист'">
    <tbody>
      <tr v-for="tier in TIERS" :key="tier">
        <th class="tier-rank" :class="`tier-${tier.toLowerCase()}`" scope="row">
          {{ tier }}
        </th>
        <td class="tier-items">
          <div class="tier-flex">
            <a
              v-for="item in byTier[tier]"
              :key="item.id"
              class="tier-item"
              :href="hrefFor(item)"
              :title="item.name"
              :target="item.maps_url ? '_blank' : undefined"
              :rel="item.maps_url ? 'noopener noreferrer' : undefined"
            >
              <img v-if="item.logo" :src="item.logo" :alt="item.name" loading="lazy" />
              <span v-else class="tier-item-text">{{ item.name }}</span>
            </a>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
table.tier-list {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 2rem;
  table-layout: fixed;
  border: 2px solid #1a1a1a;
  background: #1a1a1a;
}

table.tier-list th,
table.tier-list td {
  padding: 0;
  border: 1px solid #1a1a1a;
  vertical-align: stretch;
}

table.tier-list .tier-rank {
  width: 3.25rem;
  text-align: center;
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: #1a1a1a;
  vertical-align: middle;
}

table.tier-list .tier-s {
  background: #ff7f7f;
}
table.tier-list .tier-a {
  background: #ffbf7f;
}
table.tier-list .tier-b {
  background: #ffdf7f;
}
table.tier-list .tier-c {
  background: #ffff7f;
}
table.tier-list .tier-d {
  background: #bfff7f;
}

table.tier-list .tier-items {
  background: #2a2a2a;
}

table.tier-list .tier-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
  min-height: 3.5rem;
  padding: 0.35rem;
}

table.tier-list .tier-item {
  display: block;
  flex: 0 0 auto;
  line-height: 0;
  text-decoration: none;
}

table.tier-list .tier-item img {
  width: 50px;
  height: 50px;
  max-width: none;
  object-fit: cover;
  display: block;
  border-radius: 2px;
  margin: 0;
}

table.tier-list .tier-item:hover img {
  outline: 2px solid #fff;
  outline-offset: 1px;
}

table.tier-list .tier-item-text {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  padding: 0.25rem;
  box-sizing: border-box;
  border-radius: 2px;
  background: #3a3a3a;
  color: #eee;
  font-size: 0.55rem;
  font-weight: 600;
  line-height: 1.15;
  text-align: center;
  white-space: normal;
}

table.tier-list .tier-item:hover .tier-item-text {
  outline: 2px solid #fff;
  outline-offset: 1px;
}

@media screen and (max-width: 600px) {
  table.tier-list .tier-rank {
    width: 2.5rem;
    font-size: 1.1rem;
  }

  table.tier-list .tier-flex {
    min-height: 3.25rem;
    gap: 0.25rem;
    padding: 0.25rem;
  }
}
</style>
