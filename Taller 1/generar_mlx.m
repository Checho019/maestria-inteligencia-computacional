function generar_mlx
% Convierte los scripts T*.m a live scripts, los ejecuta y guarda los .mlx
% con las salidas y graficas adentro. Tambien exporta un PDF de cada uno.
% Es una funcion y no un script porque los T*.m empiezan con clear, y si
% esto fuera un script el clear le borraria el listado.
% Hay que correrlo desde la carpeta del taller.

scripts = {'T0_Dataset_train_test', 'T1_perceptron_compuertas', 'T2_perceptron_iris', ...
           'T3_dataset_banknote', 'T4_perceptron_banknote', 'T5_adaline_compuertas', ...
           'T6_adaline_iris', 'T7_adaline_banknote'};

if ~exist('mlx', 'dir'), mkdir('mlx'); end
if ~exist('pdf', 'dir'), mkdir('pdf'); end

for k = 1:numel(scripts)
    m   = fullfile(pwd, [scripts{k} '.m']);
    mlx = fullfile(pwd, 'mlx', [scripts{k} '.mlx']);
    pdf = fullfile(pwd, 'pdf', [scripts{k} '.pdf']);
    fprintf('\n=== %s ===\n', scripts{k});
    t = tic;
    matlab.internal.liveeditor.openAndSave(m, mlx);     % .m  -> .mlx
    matlab.internal.liveeditor.executeAndSave(mlx);     % corre y guarda con salidas
    export(mlx, pdf);                                   % .mlx -> .pdf
    fprintf('listo en %.0f s\n', toc(t));
    close all
end
disp('Todos los .mlx generados en la carpeta mlx/')
end
