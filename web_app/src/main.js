import { createApp } from "vue";
import { definePreset } from "@primevue/themes";
import App from "./App.vue";
import router from "./router";
import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";
import AnimateOnScroll from "primevue/animateonscroll";
import ToastService from "primevue/toastservice";

import Tooltip from "primevue/tooltip";

import "primeicons/primeicons.css";
import "/node_modules/primeflex/primeflex.css";
import "@/css/main.css";

const Noir = definePreset(Aura, {
  semantic: {
    primary: {
      50: "{zinc.50}",
      100: "{zinc.100}",
      200: "{zinc.200}",
      300: "{zinc.300}",
      400: "{zinc.400}",
      500: "{zinc.500}",
      600: "{zinc.600}",
      700: "{zinc.700}",
      800: "{zinc.800}",
      900: "{zinc.900}",
      950: "{zinc.950}",
    },
    colorScheme: {
      light: {
        primary: {
          color: "{zinc.950}",
          inverseColor: "#ffffff",
          hoverColor: "{zinc.900}",
          activeColor: "{zinc.800}",
        },
        highlight: {
          background: "{zinc.950}",
          focusBackground: "{zinc.700}",
          color: "#ffffff",
          focusColor: "#ffffff",
        },
      },
      dark: {
        primary: {
          color: "{zinc.50}",
          inverseColor: "{zinc.950}",
          hoverColor: "{zinc.100}",
          activeColor: "{zinc.200}",
        },
        highlight: {
          background: "rgba(250, 250, 250, .16)",
          focusBackground: "rgba(250, 250, 250, .24)",
          color: "rgba(255,255,255,.87)",
          focusColor: "rgba(255,255,255,.87)",
        },
      },
    },
  },
});

const app = createApp(App);
app
  .use(PrimeVue, {
    theme: {
      preset: Noir,
      options: {
        darkModeSelector: false || "none",
      },
    },
    locale: {
      dayNames: [
        "Воскресенье",
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
      ],
      dayNamesShort: ["Вск", "Пнд", "Втр", "Срд", "Чтв", "Птн", "Сбт"],
      dayNamesMin: ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
      monthNames: [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
      ],
      monthNamesShort: [
        "Янв",
        "Фев",
        "Мар",
        "Апр",
        "Май",
        "Июн",
        "Июл",
        "Авг",
        "Сен",
        "Окт",
        "Ноя",
        "Дек",
      ],
      firstDayOfWeek: 1,
      dateFormat: "dd.mm.yy",
      clear: "Очистить",
      editTitle: "Изменить",
      addTitle: "Добавить",
      saveTitle: "Сохранить",
      deleteTitle: "Удалить",
      cancelTitle: "Отмена",
      deleteSelected: "Удалить все выбранное",
      today: "Сегодня",
      startsWith: "Начинается с",
      contains: "Содержит",
      notContains: "Не содержит",
      endsWith: "Заканчивается на",
      equals: "Равно",
      notEquals: "Не равно",
      noFilter: "Без фильтра",
      lt: "Меньше",
      lte: "Меньше или равно",
      gt: "Больше",
      gte: "Больше или равно",
      dateIs: "Дата",
      dateIsNot: "Дата не",
      dateBefore: "Дата до",
      dateAfter: "Дата после",
      apply: "Применить",
      matchAll: "Выбрать все",
      matchAny: "Выбрать любое",
      addRule: "Добавить правило",
      removeRule: "Удалить правило",
      accept: "Да",
      reject: "Нет",
      choose: "Выбрать",
      upload: "Загрузить",
      cancel: "Отменить",
      completed: "Завершено",
      pending: "В ожидании",
      fileSizeTypes: ["Б", "КБ", "МБ", "ГБ", "ТБ", "ПБ", "ЭБ", "ЗБ", "ЙБ"],
      chooseYear: "Выбрать год",
      chooseMonth: "Выбрать месяц",
      chooseDate: "Выбрать дату",
      prevDecade: "Предыдущая декада",
      nextDecade: "Следующая декада",
      prevYear: "Предыдущий год",
      nextYear: "Следующий год",
      prevMonth: "Предыдущий месяц",
      nextMonth: "Следующий месяц",
      prevHour: "Предыдущий час",
      nextHour: "Следующий час",
      prevMinute: "Предыдущая минута",
      nextMinute: "Следующая минута",
      prevSecond: "Предыдущая секунда",
      nextSecond: "Следующая секунда",
      weekHeader: "Неделя",
      weak: "Слабый",
      medium: "Средний",
      strong: "Сильный",
      passwordPrompt: "Введите пароль",
      searchMessage: "{0} найдено",
      selectionMessage: "{0} выбрано",
      emptySelectionMessage: "Ничего не выбрано",
      emptySearchMessage: "Ничего не найдено",
      fileChosenMessage: "{0} файлов",
      noFileChosenMessage: "Нет выбраных файлов",
      emptyMessage: "Пусто",
      aria: {
        trueLabel: "True",
        falseLabel: "False",
        nullLabel: "Not Selected",
        star: "1 звезда",
        stars: "{0} звезд",
        selectAll: "Все выбрано",
        unselectAll: "Ничего не выбрано",
        close: "Закрыть",
        previous: "Предыдущий",
        next: "Следующий",
        navigation: "Навигация",
        scrollTop: "Наверх",
        scrollDown: "Вниз",
        moveTop: "Переместить вверх",
        moveDown: "Переместить вниз",
        moveBottom: "Переместить вниз",
        moveToTarget: "Переместить в цель",
        moveToSource: "Переместить в источник",
        moveAllToTarget: "Переместить все в цель",
        moveAllToSource: "Переместить все в источник",
        pageLabel: "Страница {0}",
        firstPageLabel: "Первая страница",
        lastPageLabel: "Последняя страница",
        nextPageLabel: "Следующая страница",
        previousPageLabel: "Предыдущая страница",
        rowsPerPageLabel: "Строк на странице",
        jumpToPageDropdownLabel: "Переход на страницу",
        jumpToPageInputLabel: "Переход на страницу",
        selectRow: "Выбрать строку",
        unselectRow: "Отменить выбор строки",
        expandRow: "Развернуть строку",
        collapseRow: "Свернуть строку",
        showFilterMenu: "Показать меню фильтра",
        hideFilterMenu: "Скрыть меню фильтра",
        filterOperator: "Оператор фильтра",
        filterConstraint: "Ограничение фильтра",
        editRow: "Редактировать строку",
        saveEdit: "Сохранить изменения",
        cancelEdit: "Отменить изменения",
        listView: "Посмотреть список",
        gridView: "Посмотреть сетку",
        slide: "Слайд",
        slideNumber: "{slideNumber}",
        zoomImage: "Увеличить изображение",
        zoomIn: "Увеличить",
        zoomOut: "Уменьшить",
        rotateRight: "Повернуть вправо",
        rotateLeft: "Повернуть влево",
      },
      toast: {
        severity: {
          success: "success", 
          info: "info", 
          warn: "warn", 
          error: "error"
        },
        summary: {
          success: "Успешно",
          successTitle: "Выполнено",
          info: "Информация",
          warn: "Предупреждение",
          error: "Ошибка"
        },
        detail: {
          coupons: {
            delete: "Купоны удалены",
            update: "Купоны обновлены",
          },
          coupon: {
            add: "Купон добавлен",
            edit: "Купон изменен",
            delete: "Купон удален",
          },
          privillege: {
            add: "Уровень добавлен",
            edit: "Уровень изменен",
            delete: "Уровень удален",
          },
        }
      },
    },
  })
  .use(router)
  .use(ToastService)
  .directive("animateonscroll", AnimateOnScroll)
  .directive("tooltip", Tooltip)
  .mount("#app");
