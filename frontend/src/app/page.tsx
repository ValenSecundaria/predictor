'use client';

import React, { useState } from 'react';
import {
  Container,
  Heading,
  Button,
  Box,
  SimpleGrid,
  Text,
  Card,
  CardBody,
  VStack,
  Icon,
  HStack,
  useColorModeValue,
  Flex,
} from '@chakra-ui/react';
import Link from 'next/link';
import { FaUser, FaFlask, FaTrophy, FaChartBar, FaTools } from 'react-icons/fa';

export default function Page() {
  const [mode, setMode] = useState<'usuario' | null>(null);
  const bgGradient = useColorModeValue('linear(to-br, brand.50, accent.50)', 'linear(to-br, brand.900, accent.900)');

  return (
    <Box minH="100vh" bgGradient={bgGradient} py={20}>
      <Container maxW="container.lg">
        {mode === null ? (
          <VStack spacing={12}>
            <VStack spacing={4} textAlign="center">
              <Heading
                as="h1"
                size="4xl"
                bgGradient="linear(to-r, brand.600, accent.600)"
                bgClip="text"
                fontWeight="extrabold"
                letterSpacing="tight"
              >
                Predictor Mundial
              </Heading>
              <Text fontSize="xl" color="gray.600" maxW="2xl">
                La plataforma definitiva para análisis estadístico y predicción de resultados deportivos.
                Elige tu modo para comenzar.
              </Text>
            </VStack>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={10} w="full">
              <ModeCard
                icon={FaUser}
                title="Modo Usuario"
                description="Accede a predicciones, estadísticas detalladas y análisis de equipos."
                colorScheme="brand"
                onClick={() => setMode('usuario')}
              />
              <Link href="/pruebas" style={{ textDecoration: 'none' }}>
                <ModeCard
                  icon={FaFlask}
                  title="Modo Pruebas"
                  description="Zona de desarrollo para probar nuevas funcionalidades y endpoints."
                  colorScheme="accent"
                />
              </Link>
            </SimpleGrid>
          </VStack>
        ) : (
          <VStack spacing={10}>
            <HStack w="full" justify="space-between">
              <Heading as="h2" size="xl" color="brand.700">
                Panel de Usuario
              </Heading>
              <Button variant="ghost" onClick={() => setMode(null)} leftIcon={<Icon as={FaTools} />}>
                Cambiar Modo
              </Button>
            </HStack>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8} w="full">
              <FeatureCard
                href="/equipo-ganador"
                icon={FaTrophy}
                title="Predicción de Partido"
                description="Enfrenta dos equipos y descubre quién tiene más probabilidades de ganar."
                color="brand"
              />
              <FeatureCard
                href="/estadistica-equipo"
                icon={FaChartBar}
                title="Estadísticas de Equipo"
                description="Analiza el rendimiento histórico, goles, rachas y más."
                color="accent"
              />
              {/* Placeholders for future features */}
              <FeatureCard
                icon={FaTools}
                title="Próximamente"
                description="Nuevas herramientas de análisis están en desarrollo."
                color="gray"
                isDisabled
              />
            </SimpleGrid>
          </VStack>
        )}
      </Container>
    </Box>
  );
}

const ModeCard = ({ icon, title, description, colorScheme, onClick }: any) => {
  return (
    <Card
      onClick={onClick}
      cursor={onClick || 'pointer'}
      transition="all 0.3s"
      _hover={{ transform: 'translateY(-8px)', boxShadow: '2xl' }}
      borderTopWidth={4}
      borderTopColor={`${colorScheme}.500`}
      h="full"
    >
      <CardBody p={8}>
        <VStack spacing={6} align="flex-start">
          <Flex
            w={16}
            h={16}
            align="center"
            justify="center"
            borderRadius="2xl"
            bg={`${colorScheme}.100`}
            color={`${colorScheme}.600`}
          >
            <Icon as={icon} boxSize={8} />
          </Flex>
          <Box>
            <Heading size="lg" mb={2}>{title}</Heading>
            <Text color="gray.600" fontSize="lg">{description}</Text>
          </Box>
          <Button rightIcon={<Text>→</Text>} colorScheme={colorScheme} variant="link" size="lg">
            Ingresar
          </Button>
        </VStack>
      </CardBody>
    </Card>
  );
};

const FeatureCard = ({ href, icon, title, description, color, isDisabled }: any) => {
  const CardContent = (
    <Card
      h="full"
      transition="all 0.2s"
      _hover={!isDisabled ? { transform: 'scale(1.02)', shadow: 'lg' } : {}}
      opacity={isDisabled ? 0.6 : 1}
      cursor={isDisabled ? 'not-allowed' : 'pointer'}
      bg="white"
    >
      <CardBody>
        <HStack spacing={4} align="start">
          <Flex
            shrink={0}
            w={12}
            h={12}
            align="center"
            justify="center"
            borderRadius="xl"
            bg={isDisabled ? 'gray.100' : `${color}.100`}
            color={isDisabled ? 'gray.400' : `${color}.500`}
          >
            <Icon as={icon} boxSize={6} />
          </Flex>
          <VStack align="start" spacing={1}>
            <Heading size="md">{title}</Heading>
            <Text fontSize="sm" color="gray.500">{description}</Text>
          </VStack>
        </HStack>
      </CardBody>
    </Card>
  );

  if (isDisabled || !href) return CardContent;

  return (
    <Link href={href} style={{ textDecoration: 'none' }}>
      {CardContent}
    </Link>
  );
};

