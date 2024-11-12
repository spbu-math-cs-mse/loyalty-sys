<script setup>
import { ref, onMounted } from "vue";
import { Form } from "@primevue/forms";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";
import { $dt } from "@primevue/themes";

import Chart from "primevue/chart";
import SectionHeaderInfo from "@/components/SectionHeaderInfo.vue";
import ChartNumberDisplay from "@/components/ChartNumberDisplay.vue";
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import AutoComplete from "primevue/autocomplete";

const primevue = usePrimeVue();

// function getChartColors(x, power = 500) {
//   const defaultColors = [
//     `emerald.${power}`, `green.${power}`, `lime.${power}`, `red.${power}`, `orange.${power}`, `amber.${power}`, `yellow.${power}`, `teal.${power}`, `cyan.${power}`, `blue.${power}`, `indigo.${power}`,  `violet.${power}`,
//     `purple.${power}`, `fuchsia.${power}`, `pink.${power}`, `rose.${power}`, `slate.${power}`, `gray.${power}`, `zinc.${power}`, `neutral.${power}`, `stone.${power}`
//   ];
//   const colors  = x || defaultColors;

//   let currentColor = 0;

//   return function () {
//     currentColor = (currentColor + 1) % colors.length;
//     return $dt(colors[currentColor]).value;
//   };
// }

// const getNextChartLineColors = getChartColors();

const getColorsForCharts = (count = 0, power = 500) => {
  const defaultColors = [
    `emerald.${power}`,
    `green.${power}`,
    `lime.${power}`,
    `red.${power}`,
    `orange.${power}`,
    `amber.${power}`,
    `yellow.${power}`,
    `teal.${power}`,
    `cyan.${power}`,
    `blue.${power}`,
    `indigo.${power}`,
    `violet.${power}`,
    `purple.${power}`,
    `fuchsia.${power}`,
    `pink.${power}`,
    `rose.${power}`,
    `slate.${power}`,
    `gray.${power}`,
    `zinc.${power}`,
    `neutral.${power}`,
    `stone.${power}`,
  ];

  return defaultColors.slice(0, count).map((x) => $dt(x).value);
};

onMounted(() => {
  // ProductService.getProducts().then((data) => (productList.value = data));
});

const productList = ref([
  {
    id: 1,
    name: "Молоко",
  },
  {
    id: 2,
    name: "Сыр",
  },
  {
    id: 3,
    name: "Яйца",
  },
  {
    id: 5,
    name: "Мука",
  },
]);
const selectedProductList = ref([]);
const filteredProductList = ref([]);

const searchProduct = (event) => {
  if (!event.query.trim().length) {
    filteredProductList.value = [...productList.value];
  } else {
    filteredProductList.value = productList.value.filter((product) => {
      return product.name.toLowerCase().startsWith(event.query.toLowerCase());
    });
  }
};

const onProductFormSubmit = (e) => {
  if (productDates.value[0] == null) {
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: "Выберите дату",
      life: 4000,
    });
    return;
  }
  if (selectedProductList.value.length === 0) {
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: "Выберите товар",
      life: 4000,
    });
    return;
  }
  if (productDates.value[1] == null && productDates.value[1] !== undefined) {
    productDates.value[1] = today;
  }
  if (e.valid) {
    toast.add({
      severity: "success",
      summary: "Успешно",
      detail: "Data loged to console",
      life: 4000,
    });
    console.log("Product form submitted");
    selectedProductList.value.forEach((element) => {
      console.log("id: " + element.id, element.name);
    });
    console.log(productDates.value[0], productDates.value[1]);
    setChartLineData();
  }
};

let today = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();

const productDates = ref([]);

const productMinDate = ref(new Date());
const productMaxDate = ref(new Date());

productMinDate.value.setMonth(currentMonth - 1);
productMinDate.value.setFullYear(currentYear - 1);
productMaxDate.value.setMonth(currentMonth);
productMaxDate.value.setFullYear(currentYear);

const getMonthsInRange = (fromDate, toDate) => {
  if (!fromDate || !toDate) {
    return [];
  }
  const fromYear = fromDate.getFullYear();
  const fromMonth = fromDate.getMonth();
  const toYear = toDate.getFullYear();
  const toMonth = toDate.getMonth();
  const months = [];

  for (let year = fromYear; year <= toYear; year++) {
    let monthNum = year === fromYear ? fromMonth : 0;
    const monthLimit = year === toYear ? toMonth : 11;

    for (; monthNum <= monthLimit; monthNum++) {
      months.push(primevue.config.locale.monthNames[monthNum]);
    }
  }
  return months;
};

onMounted(() => {
  chartDoughnutOptions.value = setChartOptionsDoughnut();
  chartDoughnutConfig.value = setChartConfigDoughnut();

  chartLineOptions.value = setChartOptionsLine();
  chartLineConfig.value = setChartConfigDoughnut();

  // setChartLineData();
});

const chartData = ref();

const chartDoughnutOptions = ref();
const chartDoughnutConfig = ref();

const chartLineOptions = ref();
const chartLineConfig = ref();
const chartLineData = ref();
const flag = ref(1);

const setChartConfigDoughnut = () => {
  return {
    id: "customCanvasBackgroundColor",
    beforeDraw: (chart, args, options) => {
      const { ctx } = chart;
      ctx.save();
      ctx.globalCompositeOperation = "destination-over";
      ctx.fillStyle = options.color || "#fff";
      ctx.fillRect(0, 0, chart.width, chart.height);
      ctx.restore();
    },
  };
};

const setChartDoughnutData = () => {
  const colors = [
    $dt("cyan.500").value,
    $dt("orange.500").value,
    $dt("gray.500").value,
  ];
  const hoverColors = [
    $dt("cyan.400").value,
    $dt("orange.400").value,
    $dt("gray.400").value,
  ];

  switch (flag.value) {
    case 1:
      chartData.value = {
        labels: ["Мужчины", "Женщины", "Неизвестно"],
        datasets: [
          {
            data: [540, 625, 152],
            backgroundColor: colors,
            hoverBackgroundColor: hoverColors,
            borderRadius: 2,
          },
        ],
      };
      break;

    case 2:
      chartData.value = {
        labels: ["Мужчины", "Женщины", "Хз.. Кто-то"],
        datasets: [
          {
            data: [1540, 2625, 10152],
            backgroundColor: colors,
            hoverBackgroundColor: hoverColors,
            borderRadius: 2,
          },
        ],
      };
      break;

    default:
      chartData.value = {
        labels: ["Мужчины", "Женщины", "В душе не чаю кто ты, Воин!"],
        datasets: [
          {
            data: [100, 62500, 1],
            backgroundColor: colors,
            hoverBackgroundColor: hoverColors,
            borderRadius: 2,
          },
        ],
      };
  }

  return chartData.value;
};

const setChartLineData = () => {
  const monthsInRange = getMonthsInRange(
    productDates.value[0],
    productDates.value[1]
  );
  const color = getColorsForCharts(selectedProductList.value.length);

  chartLineData.value = {
    labels: monthsInRange,
    datasets: [
      {
        label: "Товар 1",
        data: [65, 59, 80, 81, 56, 55, 40],
        fill: false,
        backgroundColor: color[0],
        borderColor: color[0],
        borderWidth: 2,
      },
      {
        label: "Товар 2",
        data: [100, 230, 5, 81, 92, 73, 37],
        fill: false,
        backgroundColor: color[1],
        borderColor: color[1],
        borderWidth: 2,
      },
    ],
  };
};

const setChartOptionsLine = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColorSecondary = documentStyle.getPropertyValue(
    "--p-text-muted-color"
  );
  const surfaceBorder = documentStyle.getPropertyValue(
    "--p-content-border-color"
  );

  const a = setChartOptionsDoughnut();
  a.plugins.title.display = false;
  a.scales = {
    x: {
      ticks: {
        color: textColorSecondary,
      },
      grid: {
        color: surfaceBorder,
      },
    },
    y: {
      ticks: {
        color: textColorSecondary,
      },
      grid: {
        color: surfaceBorder,
      },
    },
  };

  return a;
};

const setChartOptionsDoughnut = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue("--p-text-color");
  const backgroundColor = documentStyle.getPropertyValue("--p-menu-background");

  return {
    plugins: {
      legend: {
        labels: {
          usePointStyle: true,
          color: textColor,
          font: {
            family: "Montserrat",
            size: 12,
          },
        },
      },
      title: {
        display: true,
        text: "Кто чаще покупает",
        align: "start",
        color: textColor,
        padding: 8,
        font: {
          size: 18,
          family: "Montserrat",
          weight: 600,
        },
      },
      customCanvasBackgroundColor: {
        color: backgroundColor,
      },
      tooltip: {
        titleFont: {
          family: "Montserrat",
          weight: 400,
        },
        bodyFont: {
          family: "Montserrat",
          weight: 400,
        },
      },
    },
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 15,
        right: 10,
      },
    },
    responsive: true,
    aspectRatio: 2,
    maintainAspectRatio: false,
    responsiveAnimationDuration: 0,
  };
};

const toast = useToast();
</script>

<template>
  <div class="stats lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Статистика" />

    <div
      class="flex flex-wrap justify-content-around lg:justify-content-start gap-4"
    >
      <div class="border-round-lg overflow-hidden shadow-1 bg-white">
        <Chart
          type="doughnut"
          :width="500"
          :height="300"
          :data="setChartDoughnutData()"
          :plugins="[chartDoughnutConfig]"
          :options="chartDoughnutOptions"
          class=""
        />
      </div>

      <div class="flex flex-column gap-4 w-full lg:w-auto">
        <ChartNumberDisplay
          title="Cумма покупок"
          number="231654.00"
          money="₽"
          afterIcon="pi-arrow-down-right"
        />
        <ChartNumberDisplay
          title="Средний чек"
          number="4990.00"
          money="₽"
          afterIcon="pi-arrow-up-right"
        />
        <ChartNumberDisplay
          title="Поситители"
          number="546"
          beforeIcon="pi-users"
        />
      </div>

      <div class="widget border-round-lg overflow-hidden shadow-1 w-full">
        <Form
          v-slot="$form"
          @submit="onProductFormSubmit"
          class="flex flex-wrap align-items-center gap-3 mb-3"
        >
          <div class="flex flex-wrap gap-2 align-items-center">
            <label for="products_multiple" class="widget__title"
              >Статистика товара</label
            >
            <AutoComplete
              name="selectedProductList"
              v-model="selectedProductList"
              autoOptionFocus="true"
              optionLabel="name"
              inputId="products_multiple"
              :placeholder="selectedProductList.length === 0 ? 'Товар' : ''"
              :suggestions="filteredProductList"
              @complete="searchProduct"
              multiple
              forceSelection
              dropdown
              class="border-none"
            />
          </div>
          <div class="flex flex-wrap gap-2 align-items-center">
            <label for="products_range" class="widget__title">За</label>
            <DatePicker
              v-model="productDates"
              view="month"
              dateFormat="mm/yy"
              selectionMode="range"
              iconDisplay="input"
              inputId="products_range"
              name="productDates"
              :minDate="productMinDate"
              :maxDate="productMaxDate"
              showButtonBar
              showIcon
              showOtherMonths="false"
              class="max-w-12rem"
            />
          </div>
          <Button type="submit" severity="secondary" label="Показать" />
        </Form>
        <Chart
          type="line"
          :height="350"
          :data="chartLineData"
          :plugins="[chartLineConfig]"
          :options="chartLineOptions"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.widget {
  padding: 10px 15px;
  padding-top: 18px;
  background: var(--p-surface-0);
  min-width: 250px;
}

.widget__title {
  font-family: "Montserrat";
  font-size: 18px;
  font-weight: 600;
  color: var(--p-text-color);
}
</style>
