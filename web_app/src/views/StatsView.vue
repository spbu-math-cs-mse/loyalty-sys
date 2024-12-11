<script setup>
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";
import { Form } from "@primevue/forms";
import { $dt } from "@primevue/themes";

import Chart from "primevue/chart";
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import AutoComplete from "primevue/autocomplete";
import SectionHeaderInfo from "@/components/SectionHeaderInfo.vue";
import ChartNumberDisplay from "@/components/ChartNumberDisplay.vue";

const axios = require("axios");
const primevue = usePrimeVue();
const languageConfig = primevue.config.locale;

const productList = ref([]);
const selectedProductList = ref([]);
const filteredProductList = ref([]);

const searchProduct = (event) => {
  if (!event.query.trim().length) {
    filteredProductList.value = [...productList.value];
  } else {
    filteredProductList.value = productList.value.filter((product) => {
      return product.label.toLowerCase().startsWith(event.query.toLowerCase());
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

const fetchDate = ref({
  start: today.toISOString().substring(0, 7),
  end: today.toISOString().substring(0, 7),
});

const formatDateToYYYYMM = (date) => {
    return date.toLocaleString('en-CA', { year: 'numeric', month: '2-digit' }).replace('/', '-');
}

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
  chartMoreBuysOptions.value = setChartDoughnutOptions("Кто чаще покупает");
  chartBirthdayOptions.value = setChartDoughnutOptions("Дни рождения");
  chartCategoryOptions.value = setChartDoughnutOptions("Покупки в категориях");
  
  chartLineOptions.value = setChartLineOptions();
  chartLineConfig.value = setChartDoughnutConfig();
  chartDoughnutConfig.value = setChartDoughnutConfig();

  axios
    .all([
      axios.get("http://84.201.143.213:5000/data/total_purchases", {
        params: fetchDate,
      }),
      axios.get("http://84.201.143.213:5000/data/average_check", {
        params: fetchDate,
      }),
      axios.get("http://84.201.143.213:5000/data/median_check", {
        params: fetchDate,
      }),
      axios.get("http://84.201.143.213:5000/data/visitor_count", {
        params: fetchDate,
      }),
      axios.get("http://84.201.143.213:5000/data/products"),
      axios.get("http://84.201.143.213:5000/data/buys_more"),
    ])
    .then(
      axios.spread(
        (
          totalPurchasesResponse,
          averageCheckResponse,
          medianСheckResponse,
          visitorCountResponse,
          productListResponse,
          chartDataResponse
        ) => {
          totalPurchases.value = totalPurchasesResponse.data.total_purchases;
          averageCheck.value = averageCheckResponse.data.average_check;
          medianСheck.value = medianСheckResponse.data.median_check;
          visitorCount.value = visitorCountResponse.data.visitor_count;
          chartMoreBuysDataset.value = chartDataResponse.data;

          productList.value = productListResponse.data;
        }
      )
    )
    .catch((error) => {
      console.log(error);
    });
});

const totalPurchases = ref();
const averageCheck = ref();
const medianСheck = ref();
const visitorCount = ref();

const chartMoreBuysDataset = ref([]);
const chartBirthdayDataset = ref([]);
const chartCategoryDataset = ref([]);

const chartMoreBuysData = ref();
const chartBirthdayData = ref();
const chartCategoryData = ref();

const chartMoreBuysOptions = ref();
const chartBirthdayOptions = ref();
const chartCategoryOptions = ref();
const chartDoughnutConfig = ref();

const chartLineOptions = ref();
const chartLineConfig = ref();
const chartLineData = ref({});

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

const setChartDoughnutConfig = () => {
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

const setMoreBuysDoughnutData = () => {
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

  chartMoreBuysData.value = {
    labels: ["Мужчины", "Женщины", "Неизвестно"],
    datasets: [
      {
        data: chartMoreBuysDataset,
        backgroundColor: colors,
        hoverBackgroundColor: hoverColors,
        borderRadius: 2,
      },
    ],
  };

  return chartMoreBuysData.value;
};

const setBirthdayDoughnutData = () => {
  const colors = getColorsForCharts(12, 500);
  const hoverColors = getColorsForCharts(12, 400);

  chartBirthdayData.value = {
    labels: languageConfig.monthNames,
    datasets: [
      {
        data: chartBirthdayDataset,
        backgroundColor: colors,
        hoverBackgroundColor: hoverColors,
        borderRadius: 2,
      },
    ],
  };

  return chartBirthdayData.value;
};

const setCategoryDoughnutData = () => {
  const colors = getColorsForCharts(3, 500);
  const hoverColors = getColorsForCharts(3, 400);

  chartCategoryData.value = {
    labels: ['Food', 'Devices', 'Furniture'],
    datasets: [
      {
        data: chartCategoryDataset,
        backgroundColor: colors,
        hoverBackgroundColor: hoverColors,
        borderRadius: 2,
      },
    ],
  };

  return chartCategoryData.value;
};

const setChartLineData = () => {
  const monthsInRange = getMonthsInRange(
    productDates.value[0],
    productDates.value[1]
  );

  chartLineData.value.labels = monthsInRange;
  chartLineData.value.datasets = [];

  const color = getColorsForCharts(selectedProductList.value.length);

  // TODO: Remove after demo
  const data = [
    {
      dataset: [0,0,0,0,0,0,0,3,0,0,7,2,10,8],
    },
    {
      dataset: [0,0,0,0,0,0,0,0,0,0,4,0,12,15],
    },
    {
      dataset: [0,0,0,0,0,0,0,3,0,0,20,17,13,10],
    },
    {
      dataset: [0,0,0,0,0,0,0,0,1,0,2,0,3,1],
    },
    {
      dataset: [0,0,0,0,0,0,0,0,0,4,8,5,4,2],
    },
  ];

  for (let i = 0; i < selectedProductList.value.length; i++) {
    axios
      .get("http://84.201.143.213:5000/data/values", {
        params: {
          product_id: selectedProductList.value[i].id,
          start_date: formatDateToYYYYMM(productDates.value[0]),
          end_date: formatDateToYYYYMM(productDates.value[1]),
        },
      })
      .then((response) => {
        chartLineData.value.datasets.push({
          label: response.data.label,
          data: response.data.values,
          backgroundColor: color[i],
          borderColor: color[i],
          borderWidth: 2,
          fill: false,
        });
      })
      .catch((error) => {
        console.log(error);
        chartLineData.value.datasets.push({
          label: selectedProductList.value[i].label,
          data: data[i].dataset,
          backgroundColor: color[i],
          borderColor: color[i],
          borderWidth: 2,
          fill: false,
        });
      });
  }
};

const setChartLineOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColorSecondary = documentStyle.getPropertyValue(
    "--p-text-muted-color"
  );
  const surfaceBorder = documentStyle.getPropertyValue(
    "--p-content-border-color"
  );

  const a = setChartDoughnutOptions();
  // a.plugins.title.display = false;
  a.layout.padding.left = 0;
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
      min: 0,
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

const setChartDoughnutOptions = (str = "") => {
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
        display: !!str,
        text: str,
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

// TODO: Remove after demo
totalPurchases.value = 132797220;
averageCheck.value = 2567500;
medianСheck.value = 1875000;
visitorCount.value = 14;
chartMoreBuysDataset.value = [14, 27, 43];
chartBirthdayDataset.value = [1, 1, 1, 0, 2, 0, 1, 1, 3, 1, 2, 1];
chartCategoryDataset.value = [56, 18, 10];

axios.get("http://84.201.143.213:5000/data/products")
  .then((response) => {
    productList.value = response.data;
    console.log(response);
  })
  .catch((error) => {
    console.log(error);
  });

</script>

<template>
  <div class="stats container__wrapper lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Статистика" />

    <div
      class="flex flex-wrap justify-content-around lg:justify-content-start gap-4"
    >
      <div class="border-round-lg overflow-hidden shadow-1 bg-white">
        <Chart
          type="doughnut"
          :width="400"
          :height="300"
          :data="setMoreBuysDoughnutData()"
          :plugins="[chartDoughnutConfig]"
          :options="chartMoreBuysOptions"
          class=""
        />
      </div>

      <div class="border-round-lg overflow-hidden shadow-1 bg-white">
        <Chart
          type="doughnut"
          :width="400"
          :height="300"
          :data="setBirthdayDoughnutData()"
          :plugins="[chartDoughnutConfig]"
          :options="chartBirthdayOptions"
          class=""
        />
      </div>

      <div class="border-round-lg overflow-hidden shadow-1 bg-white">
        <Chart
          type="doughnut"
          :width="400"
          :height="300"
          :data="setCategoryDoughnutData()"
          :plugins="[chartDoughnutConfig]"
          :options="chartCategoryOptions"
          class=""
        />
      </div>

      <div class="flex flex-wrap gap-4 w-full">
        <ChartNumberDisplay
          title="Cумма покупок"
          :number="(totalPurchases/100).toFixed(2)"
          money="rub"
          afterIcon=""
        />
        <ChartNumberDisplay
          title="Средний чек"
          :number="(averageCheck/100).toFixed(2)"
          money="rub"
          afterIcon=""
        />
        <ChartNumberDisplay
          title="Медианный чек"
          :number="(medianСheck/100).toFixed(2)"
          money="rub"
          afterIcon=""
        />
        <ChartNumberDisplay
          title="Посетители"
          :number="visitorCount"
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
            <label for="products_multiple" class="widget__title">Продажи</label>
            <AutoComplete
              name="selectedProductList"
              v-model="selectedProductList"
              :autoOptionFocus="true"
              optionLabel="label"
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
              :showOtherMonths="false"
              class="max-w-12rem"
              placeholder="Период"
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
