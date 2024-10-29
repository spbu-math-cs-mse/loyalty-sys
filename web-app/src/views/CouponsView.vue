<script setup>
import { ref, onMounted } from "vue";
import { FilterMatchMode } from "@primevue/core/api";
import { useToast } from "primevue/usetoast";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";
import DataTable from "primevue/datatable";
import Toolbar from "primevue/toolbar";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import RadioButton from "primevue/radiobutton";
import InputNumber from "primevue/inputnumber";
import Select from "primevue/select";
import Column from "primevue/column";
import Tag from "primevue/tag";
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import Toast from "primevue/toast";

onMounted(() => {
  // ProductService.getProducts().then((data) => (products.value = data));
});

const toast = useToast();
const dt = ref();
const selectedDay = ref();
const dialogpercentSale = ref(0);
const products = ref();
const productDialog = ref(false);
const deleteProductDialog = ref(false);
const deleteProductsDialog = ref(false);
const product = ref({});
const selectedProducts = ref();
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
});
const submitted = ref(false);
const statuses = ref([
  { label: "INSTOCK", value: "instock" },
  { label: "LOWSTOCK", value: "lowstock" },
  { label: "OUTOFSTOCK", value: "outofstock" },
]);
const dialogDurationDay = ref([
  {
    label: "1 день",
    value: 1,
  },
  {
    label: "2 дня",
    value: 2,
  },
  {
    label: "3 дня",
    value: 3,
  },
  {
    label: "45 дней",
    value: 45,
  },
  {
    label: "90 дней",
    value: 90,
  },
]);

const openNew = () => {
  product.value = {};
  submitted.value = false;
  productDialog.value = true;
};
const hideDialog = () => {
  productDialog.value = false;
  submitted.value = false;
};
const saveProduct = () => {
  submitted.value = true;

  if (product?.value.name?.trim()) {
    if (product.value.id) {
      product.value.inventoryStatus = product.value.inventoryStatus.value
        ? product.value.inventoryStatus.value
        : product.value.inventoryStatus;
      products.value[findIndexById(product.value.id)] = product.value;
      toast.add({
        severity: "success",
        summary: "Successful",
        detail: "Product Updated",
        life: 3000,
      });
    } else {
      product.value.id = createId();
      product.value.code = createId();
      product.value.image = "product-placeholder.svg";
      product.value.inventoryStatus = product.value.inventoryStatus
        ? product.value.inventoryStatus.value
        : "INSTOCK";
      products.value.push(product.value);
      toast.add({
        severity: "success",
        summary: "Successful",
        detail: "Product Created",
        life: 3000,
      });
    }

    productDialog.value = false;
    product.value = {};
  }
};
const editProduct = (prod) => {
  product.value = { ...prod };
  productDialog.value = true;
};
const confirmDeleteProduct = (prod) => {
  product.value = prod;
  deleteProductDialog.value = true;
};
const deleteProduct = () => {
  products.value = products.value.filter((val) => val.id !== product.value.id);
  deleteProductDialog.value = false;
  product.value = {};
  toast.add({
    severity: "success",
    summary: "Successful",
    detail: "Product Deleted",
    life: 3000,
  });
};
const findIndexById = (id) => {
  let index = -1;
  for (let i = 0; i < products.value.length; i++) {
    if (products.value[i].id === id) {
      index = i;
      break;
    }
  }

  return index;
};
const createId = () => {
  let id = "";
  var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (var i = 0; i < 5; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return id;
};

const confirmDeleteSelected = () => {
  deleteProductsDialog.value = true;
};
const deleteSelectedProducts = () => {
  products.value = products.value.filter(
    (val) => !selectedProducts.value.includes(val)
  );
  deleteProductsDialog.value = false;
  selectedProducts.value = null;
  toast.add({
    severity: "success",
    summary: "Successful",
    detail: "Products Deleted",
    life: 3000,
  });
};

const getStatusLabel = (status) => {
  switch (status) {
    case "INSTOCK":
      return "success";

    case "LOWSTOCK":
      return "warn";

    case "OUTOFSTOCK":
      return "danger";

    default:
      return null;
  }
};

products.value = [
  {
    id: "1000",
    code: "f230fh0g3",
    name: "Bamboo Watch",
    description: "Product Description",
    image: "bamboo-watch.jpg",
    sale: 65,
    category: "Accessories",
    dayDuration: "45 дней",
    inventoryStatus: "INSTOCK",
    rating: 5,
  },
  {
    id: "1001",
    code: "f2304h0g3",
    name: "Bamboo Watch",
    description: "Product Description",
    image: "bamboo-watch.jpg",
    sale: 10,
    category: "Accessories",
    dayDuration: "1 день",
    inventoryStatus: "INSTOCK",
    rating: 5,
  },
];
</script>

<template>
  <Toast />

  <div class="coupons lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Купоны" />

    <div class="">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            label="Добавить"
            icon="pi pi-plus"
            class="mr-2"
            @click="openNew"
          />
          <Button
            label="Удалить"
            icon="pi pi-trash"
            severity="danger"
            outlined
            @click="confirmDeleteSelected"
            :disabled="!selectedProducts || !selectedProducts.length"
          />
        </template>
      </Toolbar>

      <DataTable
        ref="dt"
        :selection="selectedProducts"
        :value="products"
        dataKey="id"
        :paginator="true"
        :rows="10"
        :filters="filters"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[5, 10, 25]"
        currentPageReportTemplate="Показано {first} из {last} of {totalRecords} products"
      >
        <template #header>
          <div class="flex flex-wrap gap-2 items-center justify-between">
            <IconField>
              <InputIcon>
                <i class="pi pi-search" />
              </InputIcon>
              <InputText
                v-model="filters['global'].value"
                placeholder="Поиск..."
              />
            </IconField>
          </div>
        </template>

        <Column
          selectionMode="multiple"
          style="width: 3rem"
          :exportable="false"
        ></Column>
        <Column
          field="code"
          header="Код"
          sortable
          style="min-width: 12rem"
        ></Column>
        <Column
          field="dayDuration"
          header="Срок"
          sortable
          style="min-width: 16rem"
        ></Column>
        <Column
          field="sale"
          header="Скидка"
          sortable
          style="min-width: 8rem"
        ></Column>
        <Column
          field="status"
          header="Статус"
          sortable
          style="min-width: 12rem"
        >
          <template #body="slotProps">
            <Tag
              :value="slotProps.data.inventoryStatus"
              :severity="getStatusLabel(slotProps.data.inventoryStatus)"
            />
          </template>
        </Column>
        <Column :exportable="false" style="min-width: 12rem">
          <template #body="slotProps">
            <Button
              icon="pi pi-pencil"
              outlined
              rounded
              class="mr-2"
              @click="editProduct(slotProps.data)"
            />
            <Button
              icon="pi pi-trash"
              outlined
              rounded
              severity="danger"
              @click="confirmDeleteProduct(slotProps.data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog
      v-model:visible="productDialog"
      header="Добавить купон"
      :modal="true"
    >
      <div class="flex flex-col gap-6">
        <div class="col-span-6">
          <label for="name" class="block font-bold mb-3">Купон</label>
          <InputText
            id="name"
            v-model.trim="product.name"
            required="true"
            autofocus
            :invalid="submitted && !product.name"
            fluid
          />
          <small v-if="submitted && !product.name" class="text-red-500"
            >Это обязательное поле.</small
          >
        </div>
        <div class="col-span-6">
          <label for="percentSale" class="block font-bold mb-3"
            >Процент скидки</label
          >
          <InputNumber
            id="percentSale"
            v-model="dialogpercentSale"
            inputId="minmax-buttons"
            mode="decimal"
            showButtons
            :min="0"
            :max="100"
            fluid
          />
        </div>
        <div class="col-span-6">
          <label for="dayDuration" class="block font-bold mb-3">Срок</label>
          <Select
            id="dayDuration"
            v-model="selectedDay"
            showClear
            optionLabel="label"
            :options="dialogDurationDay"
            placeholder="1 день"
            class="w-full md:w-56"
          />
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" icon="pi pi-times" text @click="hideDialog" />
        <Button label="Save" icon="pi pi-check" @click="saveProduct" />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="deleteProductDialog"
      :style="{ width: '450px' }"
      header="Confirm"
      :modal="true"
    >
      <div class="flex items-center gap-4">
        <i class="pi pi-exclamation-triangle !text-3xl" />
        <span v-if="product"
          >Уверены, что хотите удалить <b>{{ product.name }}</b
          >?</span
        >
      </div>
      <template #footer>
        <Button
          label="No"
          icon="pi pi-times"
          text
          @click="deleteProductDialog = false"
        />
        <Button label="Yes" icon="pi pi-check" @click="deleteProduct" />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="deleteProductsDialog"
      :style="{ width: '450px' }"
      header="Confirm"
      :modal="true"
    >
      <div class="flex items-center gap-4">
        <i class="pi pi-exclamation-triangle !text-3xl" />
        <span v-if="product"
          >Уверены, что хотите удалить все выбранные купоны?</span
        >
      </div>
      <template #footer>
        <Button
          label="No"
          icon="pi pi-times"
          text
          @click="deleteProductsDialog = false"
        />
        <Button
          label="Yes"
          icon="pi pi-check"
          text
          @click="deleteSelectedProducts"
        />
      </template>
    </Dialog>
  </div>
</template>
