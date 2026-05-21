import type { ColumnDef, RowData } from "@tanstack/vue-table";

/**
 * Extended column metadata used by the shadcn-vue data-table block.
 * Keep TanStack's typing untouched; just augment via `meta`.
 */
declare module "@tanstack/vue-table" {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface ColumnMeta<TData extends RowData, TValue> {
    /** Human label shown in column-visibility toggle. */
    label?: string;
    /** Faceted filter options. If provided, header shows a dropdown with these. */
    filterOptions?: { label: string; value: string | number | boolean }[];
    /** Right-align (numeric / actions). */
    align?: "left" | "right" | "center";
    /** Add `whitespace-nowrap` to the cell (e.g. dates). */
    nowrap?: boolean;
    /** Per-cell extra class. */
    cellClass?: string;
  }
}

export type DataTableColumn<TData> = ColumnDef<TData, unknown>;
