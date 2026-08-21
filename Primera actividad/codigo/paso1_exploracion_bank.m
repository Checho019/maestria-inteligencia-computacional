%% =======================================================================
%  BANK MARKETING - Paso 0: carga, tipificacion, descriptivos y graficos
%  Se usa bank-full.csv (45211 registros, 16 predictoras + y).
%  Es el archivo completo; bank.csv es solo una muestra del 10%.
% =======================================================================
clear; clc; close all;

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'bank', 'figuras');
xls     = fullfile(base, 'Resultados_Bank.xlsx');

%% --- 1. Carga -----------------------------------------------------------
archivo = fullfile(base, 'data', 'bank', 'bank-full.csv');
T = readtable(archivo, 'Delimiter', ';', 'TextType', 'char');

num = {'age','balance','day','duration','campaign','pdays','previous'};
cat = {'job','marital','education','default','housing','loan','contact','month','poutcome'};
y   = T.y;
clase_pos = 'yes';

fprintf('Bank cargado: %d registros, %d numericas, %d categoricas\n', ...
        height(T), numel(num), numel(cat));

%% --- 2. Faltantes reales y faltantes disfrazados ------------------------
% El dataset no trae NaN, pero varias categoricas usan la etiqueta "unknown"
% que en la practica es un dato faltante. Hay que contarlo aparte.
filas = {};
for j = 1:numel(cat)
    v = T.(cat{j});
    n_unk = sum(strcmp(v, 'unknown'));
    filas(end+1,:) = {cat{j}, numel(unique(v)), n_unk, 100*n_unk/height(T)}; %#ok<SAGROW>
end
Unk = cell2table(filas, 'VariableNames', {'Variable','N_categorias','N_unknown','Pct_unknown'});
disp('--- "unknown" por variable categorica ---'); disp(Unk);
fprintf('NaN reales en las numericas: %d\n', sum(sum(ismissing(T{:, num}))));

% pdays usa -1 como "nunca lo habian contactado". Eso tampoco es un numero.
n_pdays = sum(T.pdays == -1);
fprintf('pdays = -1 (nunca contactado antes): %d registros (%.1f%%)\n', ...
        n_pdays, 100*n_pdays/height(T));

%% --- 3. Descriptivos de las numericas ----------------------------------
X = T{:, num};
Desc = table(num', mean(X)', median(X)', std(X)', min(X)', max(X)', ...
    (quantile(X,0.75) - quantile(X,0.25))', skewness(X)', kurtosis(X)', ...
    arrayfun(@(j) numel(unique(X(:,j))), (1:numel(num))'), ...
    'VariableNames', {'Variable','Media','Mediana','Desv','Min','Max','IQR', ...
                      'Asimetria','Curtosis','N_unicos'});
disp('--- Descriptivos ---'); disp(Desc);

%% --- 4. Balance de la variable objetivo (guia seccion 11) --------------
n_si = sum(strcmp(y, 'yes'));  n_no = sum(strcmp(y, 'no'));  n = height(T);
% prueba binomial exacta contra p = 0.5 (caso binario)
p_binom = 2 * min(binocdf(n_si, n, 0.5), 1 - binocdf(n_si-1, n, 0.5));
% chi2 de bondad de ajuste, por si el p binomial se va a cero por precision
chi2_bal = (n_si - n/2)^2/(n/2) + (n_no - n/2)^2/(n/2);
p_chi2 = chi2cdf(chi2_bal, 1, 'upper');
IR = n_no / n_si;

fprintf('Clase yes: %d (%.2f%%) | Clase no: %d (%.2f%%)\n', ...
        n_si, 100*n_si/n, n_no, 100*n_no/n);
% con n = 45211 los dos p-valores caen por debajo del minimo representable en
% doble precision (2.2e-308), asi que MATLAB devuelve 0 exacto. No es un error.
txt_p = sprintf('%.3g', p_binom);
if p_binom == 0, txt_p = '< 2.2e-308 (desborde de precision)'; end
fprintf('Binomial exacta contra 50/50: p = %s | Chi2 = %.1f\n', txt_p, chi2_bal);
fprintf('Razon de desbalance = %.2f a 1\n', IR);
fprintf('Un modelo que siempre diga "no" acierta el %.2f%%. Ese es el piso.\n', 100*n_no/n);

Balance = table({'no';'yes'}, [n_no; n_si], 100*[n_no; n_si]/n, ...
    'VariableNames', {'Clase','N','Porcentaje'});
Bal_test = table({'p_binomial';'chi2';'p_chi2';'IR';'Tasa_base_no';'N_total'}, ...
                 [p_binom; chi2_bal; p_chi2; IR; n_no/n; n], ...
                 'VariableNames', {'Indicador','Valor'});

%% --- 5. Graficos --------------------------------------------------------
% 5.1 histogramas
f = figure('Visible','off','Position',[100 100 1250 600]);
for j = 1:numel(num)
    subplot(2,4,j);
    histogram(X(:,j), 50, 'FaceColor',[0.2 0.5 0.8]);
    title(sprintf('%s (asim=%.1f)', num{j}, skewness(X(:,j)))); ylabel('frec');
end
sgtitle('Bank - histogramas de las variables numericas (dato crudo)');
guardar_fig(f, dir_fig, '01_histogramas_crudo');

% 5.2 boxplots, uno por variable y no todos juntos: balance llega a 102.000
% y duration a 4.918, asi que en un solo eje aplastarian a las demas.
f = figure('Visible','off','Position',[100 100 1250 500]);
for j = 1:numel(num)
    subplot(2,4,j);
    boxplot(X(:,j)); title(num{j}); ylabel('valor');
end
sgtitle('Bank - boxplots de las numericas (dato crudo, regla 1.5*IQR)');
guardar_fig(f, dir_fig, '02_boxplot_crudo');

% 5.3 balance de clase
f = figure('Visible','off','Position',[100 100 700 420]);
bar(categorical({'no','yes'}), [n_no n_si], 'FaceColor',[0.85 0.4 0.3]);
text(1:2, [n_no n_si]+800, compose('%d (%.1f%%)', [n_no; n_si], 100*[n_no; n_si]/n), ...
     'HorizontalAlignment','center');
ylabel('numero de clientes'); ylim([0 45000]);
title('Bank - la clase objetivo esta desbalanceada 7.5 a 1');
guardar_fig(f, dir_fig, '03_balance_clases_crudo');

% 5.4 boxplot de cada numerica separada por clase
f = figure('Visible','off','Position',[100 100 1250 600]);
for j = 1:numel(num)
    subplot(2,4,j);
    boxplot(X(:,j), y); title(num{j}); ylabel('valor');
end
sgtitle('Bank - numericas por clase (respaldo visual de Mann-Whitney/Welch)');
guardar_fig(f, dir_fig, '04_boxplot_por_clase');

% 5.5 Q-Q plots
f = figure('Visible','off','Position',[100 100 1250 600]);
for j = 1:numel(num)
    subplot(2,4,j); qqplot(X(:,j)); title(num{j});
    xlabel('cuantiles teoricos'); ylabel('muestra');
end
sgtitle('Bank - Q-Q plots contra la normal');
guardar_fig(f, dir_fig, '05_qqplots');

% 5.6 tasa de "yes" por categoria: es la forma mas clara de ver si una
% categorica sirve para separar la clase
f = figure('Visible','off','Position',[100 100 1300 750]);
for j = 1:numel(cat)
    subplot(3,3,j);
    v = T.(cat{j});
    niveles = unique(v);
    tasa = cellfun(@(lv) mean(strcmp(y(strcmp(v,lv)), 'yes')), niveles);
    [tasa, o] = sort(tasa, 'descend');
    bar(categorical(niveles(o), niveles(o)), 100*tasa, 'FaceColor',[0.35 0.6 0.75]);
    hold on; yline(100*n_si/n, 'r--');
    % title(cat(j)) con llaves y no title(cat{j}): 'default' es palabra
    % reservada de los graficos y si se pasa como texto suelto no dibuja nada
    title(cat(j)); ylabel('% que dice si');
    set(gca, 'XTickLabelRotation', 45, 'FontSize', 7);
end
sgtitle('Bank - tasa de contratacion por categoria (linea roja = tasa global 11.7%)');
guardar_fig(f, dir_fig, '06_tasa_por_categoria');

%% --- 6. Exportar --------------------------------------------------------
writetable(Desc,     xls, 'Sheet', 'B1_Descriptivos');
writetable(Unk,      xls, 'Sheet', 'B1_Unknown');
writetable(Balance,  xls, 'Sheet', 'B1_Balance_clase');
writetable(Bal_test, xls, 'Sheet', 'B1_Balance_test');

save(fullfile(base,'resultados','bank','bank_crudo.mat'), 'T','num','cat','y','clase_pos');
fprintf('\nPaso 1 (exploracion bank) terminado.\n');
