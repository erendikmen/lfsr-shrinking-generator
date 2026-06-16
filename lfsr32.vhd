library ieee;
use ieee.std_logic_1164.all;

entity lfsr32 is
  port(
    clk    : in  std_logic;
    rst_n  : in  std_logic;
    en     : in  std_logic := '1';
    load   : in  std_logic := '0';
    seed   : in  std_logic_vector(31 downto 0) := (others => '1'); 
    q      : out std_logic_vector(31 downto 0);
    bit_o  : out std_logic
  );
end entity;

architecture rtl of lfsr32 is
  signal r : std_logic_vector(31 downto 0) := (others => '1');
begin
  q     <= r;
  bit_o <= r(0);

  process(clk, rst_n)
    variable feedback : std_logic;
  begin
    if rst_n = '0' then
      r <= (others => '1');
    elsif rising_edge(clk) then
      if load = '1' then
        if seed = (seed'range => '0') then
          r <= (others => '1');
        else
          r <= seed;
        end if;
      elsif en = '1' then
        -- PRBS32: x^32 + x^22 + x^2 + x + 1 -> taps: 32,22,2,1
        feedback := r(0) xor r(1) xor r(2) xor r(22);
        r <= feedback & r(31 downto 1);
      end if;
    end if;
  end process;
end architecture;
