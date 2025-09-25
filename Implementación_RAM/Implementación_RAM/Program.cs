using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;

class WindowsMemoryMonitor
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    private class MEMORYSTATUSEX
    {
        public uint dwLength;
        public uint dwMemoryLoad;
        public ulong ullTotalPhys;
        public ulong ullAvailPhys;
        public ulong ullTotalPageFile;
        public ulong ullAvailPageFile;
        public ulong ullTotalVirtual;
        public ulong ullAvailVirtual;
        public ulong ullAvailExtendedVirtual;

        public MEMORYSTATUSEX()
        {
            dwLength = (uint)Marshal.SizeOf(typeof(MEMORYSTATUSEX));
        }
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern bool GlobalMemoryStatusEx([In, Out] MEMORYSTATUSEX lpBuffer);

    private MEMORYSTATUSEX memoryStatus = new MEMORYSTATUSEX();

    public double GetMemoryUsedMB()
    {
        GlobalMemoryStatusEx(memoryStatus);
        return (memoryStatus.ullTotalPhys - memoryStatus.ullAvailPhys) / (1024.0 * 1024.0);
    }

    public double GetMemoryTotalMB()
    {
        GlobalMemoryStatusEx(memoryStatus);
        return memoryStatus.ullTotalPhys / (1024.0 * 1024.0);
    }

    public double GetMemoryAvailableMB()
    {
        GlobalMemoryStatusEx(memoryStatus);
        return memoryStatus.ullAvailPhys / (1024.0 * 1024.0);
    }

    public double GetMemoryUsagePercentage()
    {
        GlobalMemoryStatusEx(memoryStatus);
        return memoryStatus.dwMemoryLoad;
    }

    public void DisplayMemoryInfo()
    {
        double used = GetMemoryUsedMB();
        double total = GetMemoryTotalMB();
        double available = GetMemoryAvailableMB();
        double percentage = GetMemoryUsagePercentage();

        Console.Clear();
        Console.WriteLine("======================================");
        Console.WriteLine("        MONITOR DE MEMORIA RAM");
        Console.WriteLine("======================================");
        Console.WriteLine($"Memoria Usada:       {used:F2} MB");
        Console.WriteLine($"Memoria Total:       {total:F2} MB");
        Console.WriteLine($"Memoria Disponible:  {available:F2} MB");

        // Selección de color según uso
        if (percentage < 80)
            Console.ForegroundColor = ConsoleColor.Green;
        else if (percentage < 90)
            Console.ForegroundColor = ConsoleColor.Yellow;
        else
            Console.ForegroundColor = ConsoleColor.Red;

        Console.WriteLine($"Porcentaje de Uso:   {percentage:F1}%");

        // Barra de progreso
        Console.Write("[");
        int bars = (int)(percentage / 2); // escala: 50 barras
        for (int i = 0; i < 50; i++)
        {
            if (i < bars) Console.Write("|");
            else Console.Write(" ");
        }
        Console.WriteLine("]");

        // Reset color
        Console.ResetColor();
        Console.WriteLine("======================================");
    }
}

class Program
{
    static void Main()
    {
        WindowsMemoryMonitor monitor = new WindowsMemoryMonitor();

        Console.WriteLine("Iniciando monitor de memoria RAM...");
        Console.WriteLine("Presiona Ctrl+C para detener");
        Thread.Sleep(2000);

        while (true)
        {
            monitor.DisplayMemoryInfo();
            Thread.Sleep(1000); // cada 10 segundos
        }
    }
}
